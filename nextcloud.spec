# based my build for stella. symbianflo

%if %{_use_internal_dependency_generator}
%define __noautoreq /usr/bin/php
%else
%define _requires_exceptions /usr/bin/php
%endif

Summary:	Private file sync and share server
Name:		nextcloud
Version:	30.0.4
Release:	1
Source0:	https://download.nextcloud.com/server/releases/%{name}-%{version}.tar.bz2
Source1:	apache.example.conf
Source2:	nextcloud.conf
Source3:	nextcloud-subdir.conf
Source100:	%{name}.rpmlintrc

License:	AGPLv3
Group:		Monitoring
Url:		https://nextcloud.com/

# perl
Requires:	perl(Locale::PO)
Requires:	perl(Cwd)
Requires:	perl(Data::Dumper)
Requires:	perl(File::Basename)
Requires:	perl(File::Path)
Requires:	perl(Locale::PO)
# CLI is required for the cron jobs/timers
Requires:	php-cli >= 4.1
# php libs
Requires:	config(php-zip)
Requires:	config(php-mbstring)
Requires:	config(php-gd)
Requires:	config(php-curl)
Requires:	config(php-iconv)
Requires:	config(php-sqlite3)
Requires:	config(php-pdo_sqlite)
Requires:	config(php-pgsql)
Requires:	config(php-ldap)
Requires:	config(php-intl)
Recommends:	php-bz2
Recommends:	php-gmp
Recommends:	php-bcmath
Recommends:	php-opcache
# sqlite is sufficient, but Postgres or MariaDB/MySQL are preferred
# for real world workloads
Recommends:	(config(php-pdo_pgsql) or config(php-pdo_mysql))
#  drop cacheing because of conflicts,Sflo
# Suggests:     config(php-xcache)
Requires:	samba-client

# files preview
Requires:	ffmpeg
Suggests:	libreoffice

BuildArch:	noarch

Requires(post):	%{_bindir}/runuser
Requires(post):	php-cli
Requires(post):	user(www)

%description
A personal cloud server which runs on you personal server 
and enables accessing your data from everywhere and sharing 
with other people.

%package apache
Summary:	Configuration files etc. for running NextCloud with the Apache web server
Group:		Servers
# apache
Requires:	config(apache-base)
Requires:	config(apache-mod_php)

%description apache
Configuration files etc. for running NextCloud with the Apache web server

%files apache
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf

%package nginx
Summary:	Configuration files etc. for running NextCloud with the NGINX web server
Group:		Servers
Requires:	nginx
Requires:	php-nginx

%description nginx
Configuration files etc. for running NextCloud with the NGINX web server

%files nginx
%{_sysconfdir}/nginx/nextcloud.conf
%{_sysconfdir}/nginx/nextcloud-subdir.conf

%files
%doc AUTHORS 
%attr(-,www,www) /srv/%{name}
%ghost /srv/%{name}/updater/update-%{version}-%{release}.log
%{_unitdir}/nextcloudcron.service
%{_unitdir}/nextcloudcron.timer
#--------------------------------------------------------------------


%prep
%autosetup -p1 -n %{name}

%build

%install
mkdir -p %{buildroot}/srv
(
cd %{buildroot}/srv
tar xf %{S:0}
)

# install apache config file
install -D -m 644 %{S:1}  %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf

# NGINX config file
mkdir -p %{buildroot}%{_sysconfdir}/nginx
install -D -m 644 %{S:2} %{buildroot}%{_sysconfdir}/nginx/nextcloud.conf
install -D -m 644 %{S:3} %{buildroot}%{_sysconfdir}/nginx/nextcloud-subdir.conf

# Timers
mkdir -p %{buildroot}%{_unitdir}

cat >%{buildroot}%{_unitdir}/nextcloudcron.service <<EOF
[Unit]
Description=Nextcloud cron.php job

[Service]
User=www
ExecCondition=/usr/bin/php -f /srv/nextcloud/occ status -e
ExecStart=/usr/bin/php -f /srv/nextcloud/cron.php
KillMode=process
EOF

cat >%{buildroot}%{_unitdir}/nextcloudcron.timer <<EOF
[Unit]
Description=Run Nextcloud cron.php every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=nextcloudcron.service

[Install]
WantedBy=timers.target
EOF

# fix some attr
find %{buildroot}/srv/nextcloud -type f -exec chmod 0644 {} \;
find %{buildroot}/srv/nextcloud -type d -exec chmod 0755 {} \;

%post
if [ "$1" -ge 2 ]; then
	pushd /srv/nextcloud &>/dev/null
	runuser -u www -- %{_bindir}/php --define apc.enable_cli=1 ./occ upgrade &>updater/update-%{version}-%{release}.log
	popd &>/dev/null
fi
