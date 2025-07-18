# TODO
# - add R dojo http://dojotoolkit.org/
# - upgrade.php
# - proper webapps integration: make config not accessible from web
# - proper patch for system adodb (i.e not symlink)
# - fork fruity to lilac - http://www.lilacplatform.net/
%define		_rc rc2
%define		_rel 0.2
Summary:	Nagios Configuration Tool
Summary(pl.UTF-8):	Narzędzie konfiguracyjne dla Nagiosa
Name:		nagios-fruity
Version:	1.0
Release:	0.%{_rc}.%{_rel}
License:	GPL v2
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/fruity/fruity-%{version}-%{_rc}.tar.gz
# Source0-md5:	2c4fd0ad1d58c47f37e8dd64f61bfdce
Patch0:		%{name}-adodb.patch
Patch1:		%{name}-config.patch
URL:		http://fruity.sourceforge.net/
BuildRequires:	rpmbuild(macros) >= 1.264
BuildRequires:	sed >= 4.0
Requires:	adodb >= 4.67-1.17
Requires:	nagios >= 2.0-0.b4
Requires:	php(mysql)
Requires:	php-pear-HTML_TreeMenu
Requires:	php-pear-DB_odbtp
Requires:	webapps
Requires:	webserver(php) >= 5.0.0
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		fruity
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
Fruity is an open-source web-based configuration tool for the Nagios
network monitoring system. It is designed to provide a logical process
of creating and managing your network. It is written in PHP and uses
the AdoDB database abstraction library.

%description -l pl.UTF-8
Fruity to otwarte obsługiwane przez WWW narzędzie konfiguracyjne dla
systemu monitorowania sieci Nagios. Zostało zaprojektowane aby
zapewnić logiczny proces tworzenia i zarządzania siecią. Jest napisane
w PHP i wykorzystuje bibliotekę abstrakcji baz danych AdoDB.

%prep
%setup -q -n fruity-%{version}-%{_rc}

mv includes/config.inc{,.dist}
rm -rf includes/adodb # using system adodb

# undos the source
find '(' -name '*.php' -o -name '*.inc' ')' -print0 | xargs -0 sed -i -e 's,\r$,,'

%patch -P0 -p1
%patch -P1 -p1

cat <<EOF > apache.conf
Alias /fruity %{_appdir}
<Location /fruity>
	allow from all
	php_value short_open_tag on
</Location>
EOF

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}}

cp -a *.php *.js $RPM_BUILD_ROOT%{_appdir}
cp -a images includes modules output sitedb style $RPM_BUILD_ROOT%{_appdir}
cp apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

sed -e "
s,%{_prefix}/local/groundwork/fruity/logos,%{_datadir}/nagios/images/logos,
s,%{_prefix}/local/groundwork/fruity,%{_datadir}/fruity,
s,sitedb_config\[.username.\].=.'root',sitedb_config['username'] = 'mysql',
" includes/config.inc.dist > $RPM_BUILD_ROOT%{_appdir}/includes/config.inc

rm -f $RPM_BUILD_ROOT%{_appdir}/includes/config.inc.dist

# config
mv -f $RPM_BUILD_ROOT%{_appdir}/includes/config.inc $RPM_BUILD_ROOT%{_sysconfdir}/fruity.php
ln -s %{_sysconfdir}/fruity.php $RPM_BUILD_ROOT%{_appdir}/includes/config.inc
ln -s %{php_data_dir}/adodb $RPM_BUILD_ROOT%{_appdir}/includes/adodb

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = 1 ]; then
	%banner %{name} <<-EOF
	You need to create mysql database 'fruity':
	mysqladmin create fruity
	zcat %{_docdir}/%{name}-%{version}/fruity-mysql.sql.gz | mysql fruity
EOF
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc INSTALL sqldata/*
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fruity.php
%{_appdir}
