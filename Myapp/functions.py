import os
import sys
from datetime import datetime, timedelta

from django.db.models import Avg, Count, DateField, F, Max, Min, Q, Sum
from django.utils import timezone

from . import models


def ShowException(exceptionMsg):
  exception_type, exception_object, exception_traceback = sys.exc_info()
  filename = exception_traceback.tb_frame.f_code.co_filename
  line_number = exception_traceback.tb_lineno
  print("Exception: ", exception_object)
  print("File name: ", filename)
  print("Line number: ", line_number)