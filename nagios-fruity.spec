Summary:	Nagios Configuration Tool
Summary(pl):	Narzêdzie konfiguracyjne dla Nagiosa
Name:		nagios-fruity
Version:	1.0
%define		_beta beta2
%define		_rc pl1
%define		_rel 1
Release:	0.%{_beta}.%{_rc}.%{_rel}
License:	GPL v2
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/fruity/fruity-%{version}-%{_beta}-%{_rc}.tar.gz
# Source0-md5:	92a51b947ac4a8f36119f273592b415d
URL:		http://fruity.sourceforge.net/
BuildRequires:	rpmbuild(macros) >= 1.226
BuildRequires:	sed >= 4.0
Requires:	adodb
Requires:	nagios >= 2.0-0.b4
Requires:	php >= 4:5.0.0
Requires:	php-mysql
Requires:	php-pear-HTML_TreeMenu
Requires:	webserver = apache
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir /etc/fruity
%define		_appdir %{_datadir}/fruity

%description
A Nagios Configuration Tool.

%description
Narzêdzie konfiguracyjne dla Nagiosa.

%prep
%setup -q -n fruity
rm -rf CVS
rm -rf config # no longer used

# undos the source
find '(' -name '*.php' -o -name '*.inc' ')' -print0 | xargs -0 sed -i -e 's,
$,,'

mv includes/config.inc{,.dist}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}}

cp -a *.php *.js $RPM_BUILD_ROOT%{_appdir}
cp -a images includes modules output sitedb style $RPM_BUILD_ROOT%{_appdir}

cat <<EOF > $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
Alias /fruity %{_appdir}
<Location /fruity>
	allow from all
	php_value short_open_tag on
</Location>
# vim: filetype=apache ts=4 sw=4 et
EOF

sed -e "
s,%{_prefix}/local/groundwork/fruity/logos,%{_datadir}/nagios/images/logos,
s,%{_prefix}/local/groundwork/fruity,%{_datadir}/fruity,
s,sitedb_config\[.username.\].=.'root',sitedb_config['username'] = 'mysql',
" includes/config.inc.dist > $RPM_BUILD_ROOT%{_appdir}/includes/config.inc

rm -f $RPM_BUILD_ROOT%{_appdir}/includes/config.inc.dist

# config
mv -f $RPM_BUILD_ROOT%{_appdir}/includes/config.inc $RPM_BUILD_ROOT%{_sysconfdir}/fruity.php
ln -s %{_sysconfdir}/fruity.php $RPM_BUILD_ROOT%{_appdir}/includes/config.inc

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

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%files
%defattr(644,root,root,755)
%doc INSTALL sqldata/*
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fruity.php
%{_appdir}
