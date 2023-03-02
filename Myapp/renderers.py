from rest_framework import renderers
import json
from django.shortcuts import redirect, render , get_object_or_404



class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''
        if 'ErrorDetail' in str(data):
            response = json.dumps({'errors': data})
            return redirect("/login/")
 
        else:
            response = json.dumps({'data': data})
        return response
