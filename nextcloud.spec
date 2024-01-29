# based my build for stella. symbianflo

%if %{_use_internal_dependency_generator}
%define __noautoreq /usr/bin/php
%else
%define _requires_exceptions /usr/bin/php
%endif

Summary:	Private file sync and share server
Name:		nextcloud
Version:	28.0.1
Release:	2
Source0:	https://download.nextcloud.com/server/releases/%{name}-%{version}.tar.bz2
Source1:	apache.example.conf
Source2:	nextcloud.conf
Source100:	%{name}.rpmlintrc

License:	AGPLv3
Group:		Monitoring
Url:		http://nextcloud.com/

# perl
Requires:	perl(Locale::PO)
Requires:	perl(Cwd)
Requires:	perl(Data::Dumper)
Requires:	perl(File::Basename)
Requires:	perl(File::Path)
Requires:	perl(Locale::PO)
#php
Requires:	php-cli >= 4.1
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
#  drop cacheing because of conflicts,Sflo
# Suggests:     config(php-xcache)
Requires:	mariadb
Requires:	samba-client

# files preview
Requires:	ffmpeg
Suggests:	libreoffice

BuildArch:	noarch

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

%description nginx
Configuration files etc. for running NextCloud with the NGINX web server

%files nginx
%{_sysconfdir}/nginx/nextcloud.conf

%files
%doc AUTHORS 
%attr(-,www,www) /srv/%{name}
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

# fix some attr
find %{buildroot}/srv/nextcloud -type f -exec chmod 0644 {} \;
find %{buildroot}/srv/nextcloud -type d -exec chmod 0755 {} \;
