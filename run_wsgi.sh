#!/bin/bash

gunicorn first.wsgi:application
