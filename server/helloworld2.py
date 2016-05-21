import config
import logging as logger
import json

from server import api
from flask import Blueprint, Flask, redirect, request, Response, url_for
from .model_mongodb import MongoDB

logger.info(" helloworld2 imported")