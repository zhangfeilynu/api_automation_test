import logging

from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.models import Project, GlobalHost, ProjectDynamic
from api_test.serializers import GlobalHostSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(["GET"])
@verify_parameter(["project_id", ], "GET")
def host_total(request):
    """
    获取host列表
    project_id 项目ID
    :return:
    """
    try:
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        name = request.GET.get("name")
        if name:
            obi = GlobalHost.objects.filter(name__contains=name, project=project_id).order_by("id")
        else:
            obi = GlobalHost.objects.filter(project=project_id).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = GlobalHostSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "name", "host"], "POST")
def add_host(request):
    """
    新增host
    project_id 项目ID
    name host名称
    host host地址
    description host描述
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    name = request.POST.get("name")
    host = request.POST.get("host")
    desc = request.POST.get("description")
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(name=name, project=project_id)
        if obi:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            hosts = GlobalHost(project=Project.objects.get(id=project_id), name=name, host=host, description=desc)
            hosts.save()
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type="新增",
                                    operationObject="HOST", user=User.objects.get(id=request.user.pk),
                                    description="新增HOST“%s”" % name)
            record.save()
            return JsonResponse(data={
                "host_id": hosts.pk
            }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "host_id", "name", "host"], "POST")
def update_host(request):
    """
    修改host
    project_id 项目id
    host_id 地址ID
    name 地址名称
    host 地址域名
    description 描述
    :return:
    """
    project_id = request.POST.get("project_id")
    host_id = request.POST.get("host_id")
    if not host_id.isdecimal() or not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    name = request.POST.get("name")
    host = request.POST.get("host")
    desc = request.POST.get("description")
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obm = GlobalHost.objects.filter(name=name).exclude(id=host_id)
            if len(obm) == 0:
                obi.update(project=Project.objects.get(id=project_id), name=name, host=host, description=desc)
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type="修改",
                                        operationObject="HOST", user=User.objects.get(id=request.user.pk),
                                        description="修改HOST“%s”" % name)
                record.save()
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "ids"], "POST")
def del_host(request):
    """
    删除host
    project_id  项目ID
    ids 地址ID
    :return:
    """
    project_id = request.POST.get("project_id")
    ids = request.POST.get("ids")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    id_list = ids.split(",")
    for i in id_list:
        if not i.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        for j in id_list:
            obi = GlobalHost.objects.filter(id=int(j), project=project_id)
            if obi:
                obi.delete()
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "host_id"], "POST")
def disable_host(request):
    """
    禁用host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    project_id = request.POST.get("project_id")
    host_id = request.POST.get("host_id")
    if not project_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obi.update(status=False)
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type="禁用",
                                    operationObject="HOST", user=User.objects.get(id=request.user.pk),
                                    description="禁用HOST“%s”" % obi[0].name)
            record.save()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "host_id"], "POST")
def enable_host(request):
    """
    启用host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    project_id = request.POST.get("project_id")
    host_id = request.POST.get("host_id")
    if not project_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obi.update(status=True)
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type="启用",
                                    operationObject="HOST", user=User.objects.get(id=request.user.pk),
                                    description="启用HOST“%s”" % obi[0].name)
            record.save()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
