

root='./task'

su ops -c " cd $root ;  celery worker -c 5 -l info "
