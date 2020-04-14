FROM centos/systemd

RUN yum -y install epel-release
RUN yum -y install nginx
RUN yum -y install git
RUN yum -y install python3-devel
RUN yum -y install rpm-build

RUN git config --global user.name "Ilya Zvezdin"
RUN git config --global user.email mail@mail.com
RUN git clone https://github.com/isz/wsgi_daemon.git /tmp/ip2w
RUN chmod +x /tmp/ip2w/buildrpm.sh
RUN cd /tmp/ip2w; ./buildrpm.sh /tmp/ip2w/ip2w.spec

