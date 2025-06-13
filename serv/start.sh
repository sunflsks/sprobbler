#!/usr/bin/env sh

if [[ -z "${SPROBBLER_DEBUG}" ]]; then
	uv run supervisord -c supervisord.conf
else
	uv run scripts/start_debug.py
fi
