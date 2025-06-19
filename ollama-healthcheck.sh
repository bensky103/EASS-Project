#!/bin/sh
timeout 1 bash -c ">/dev/tcp/localhost/11434" && exit 0 || exit 1 