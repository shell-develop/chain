from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, View, CreateView, UpdateView
from django.urls import reverse_lazy
from name.form import NameForm, GroupsForm, GroupsObjectForm
from name.models import Names, Groups
from guardian.models import GroupObjectPermission
import json
import logging

logger = logging.getLogger('name')
from django.utils.decorators import method_decorator
from guardian.shortcuts import assign_perm, get_perms
from guardian.core import ObjectPermissionChecker
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user, get_objects_for_group


class NameListAll(LoginRequiredMixin, ListView):
    """资产列表"""
    template_name = 'name/name.html'
    model = Names
    context_object_name = "name_list"
    queryset = Names.objects.all()
    ordering = ('id',)

    @method_decorator(permission_required_or_403('name.add_names'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "name_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class NameAdd(LoginRequiredMixin, CreateView):
    """
    登录用户增加
    """
    model = Names
    form_class = NameForm
    template_name = 'name/name-add-update.html'
    success_url = reverse_lazy('name:name_list')

    @method_decorator(permission_required_or_403('name.add_names'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "name_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        forms = form.save()
        password_form = form.cleaned_data['password']
        if password_form is not None:
            forms.set_password(password_form)
            forms.save()
        return super().form_valid(form)


class NameUpdate(LoginRequiredMixin, UpdateView):
    """登录用户更新"""

    model = Names
    form_class = NameForm
    template_name = 'name/name-add-update.html'
    success_url = reverse_lazy('name:name_list')

    @method_decorator(permission_required_or_403('name.change_names'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "name_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        obj = Names.objects.get(id=pk)
        old_password = obj.password
        new_password = form.cleaned_data['password']

        forms = form.save()
        if new_password == "1":
            forms.password = old_password
        else:
            forms.set_password(new_password)
        forms.save()
        return super().form_valid(form)


class NameAllDel(LoginRequiredMixin, View):
    """
    系统用户删除
    """
    model = Names

    @method_decorator(permission_required_or_403('name.delete_names'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                Names.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                Names.objects.extra(
                    where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class GroupListAll(LoginRequiredMixin, ListView):
    """系统组列表"""

    template_name = 'name/groups.html'
    model = Groups
    context_object_name = "groups_list"
    queryset = Groups.objects.all()
    ordering = ('id',)

    @method_decorator(permission_required_or_403('name.add_groups'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "groups_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GroupsAdd(LoginRequiredMixin, CreateView):
    """
    系统组增加
    """
    model = Groups
    form_class = GroupsForm
    template_name = 'name/groups-add-update.html'
    success_url = reverse_lazy('name:groups_list')

    @method_decorator(permission_required_or_403('name.add_groups'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "groups_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GroupsUpdate(LoginRequiredMixin, UpdateView):
    """系统组更新"""

    model = Groups
    form_class = GroupsForm
    template_name = 'name/groups-add-update.html'
    success_url = reverse_lazy('name:groups_list')

    @method_decorator(permission_required_or_403('name.change_groups'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "groups_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GroupsAllDel(LoginRequiredMixin, View):
    """
    系统组删除
    """
    model = Groups

    @method_decorator(permission_required_or_403('name.delete_groups'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                Groups.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                Groups.objects.extra(
                    where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class GroupObjectListAll(LoginRequiredMixin, ListView):
    """系统组 对象 列表"""

    template_name = 'name/groups-object.html'
    model = GroupObjectPermission
    context_object_name = "groups_object_list"
    queryset = GroupObjectPermission.objects.all()
    ordering = ('id',)

    @method_decorator(permission_required_or_403('guardian.add_groupobjectpermission'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "groups_object_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GroupsObjectAdd(LoginRequiredMixin, CreateView):
    """
    系统组对象 增加
    """
    model = GroupObjectPermission
    form_class = GroupsObjectForm
    template_name = 'name/groups-object-add-update.html'
    success_url = reverse_lazy('name:groups_object_list')

    @method_decorator(permission_required_or_403('guardian.add_groupobjectpermission'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "groups_object_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        forms = form.save(commit=False)
        obj = form.cleaned_data['object_pk1']
        forms.object_pk = obj
        forms.save()
        return super().form_valid(form)


class GroupsObjectAllDel(LoginRequiredMixin, View):
    """
    系统组删除
    """
    model = GroupObjectPermission

    @method_decorator(permission_required_or_403('guardian.delete_groupobjectpermission'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                GroupObjectPermission.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                GroupObjectPermission.objects.extra(
                    where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class GroupsObjectUpdate(LoginRequiredMixin, UpdateView):
    """系统组更新"""

    model = GroupObjectPermission
    form_class = GroupsObjectForm
    template_name = 'name/groups-object-add-update.html'
    success_url = reverse_lazy('name:groups_object_list')

    @method_decorator(permission_required_or_403('guardian.change_groupobjectpermission'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "groups_object_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
