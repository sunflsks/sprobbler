#!/usr/bin/env sh

export PYTHONPATH="$PWD"

if [[ -z "${SPROBBLER_DEBUG}" ]]; then
	"$VENVPATH/bin/supervisord" -c supervisord.conf
else
	"$VENVPATH/bin/python" scripts/start_debug.py
fi
