FROM  redis:3.2.10-alpine
#FROM 45c3ea2cecac
MAINTAINER paco.li paco.li@ericsdad.com
#RUN yum -y install perl iproute
COPY ./redis.conf /usr/local/bin/redis.conf
COPY ./run.sh /usr/local/bin/run.sh
CMD ["/usr/local/bin/run.sh"]
