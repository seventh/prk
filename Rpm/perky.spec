summary:       Management of software requirements with any SCM
summary(fr):   Gestionnaire d'exigences logiciels basé sur n'importe quel GCL
name:          perky
epoch:         1
version:       1404190
release:       0%{?dist}
group:         Development/Tools
license:       CeCILL
url:           http://github.com/seventh/prk

source:        %{name}-%{version}.tar.bz2
buildarch:     noarch

requires:      python3

requires:      pandoc
requires:      python-docutils

%description
PeRKy is a computer software dedicated to management of software requirements with any Source Control Manager (abbreviated SCM) as storage layer, based on a simple principle: 1 file per requirement.

PeRKy helps users to keep documentation in sync with their developments by using the same tools than the one they use for code. It also integrates notions of distributed development and thus highly limitates the risk of encountering conflicts when merging branches of development.

%description -l fr
PeRKy est un programme dédié à faciliter la gestion des exigences logicielles, utilisant comme moteur de stockage le Gestionnaire de Configuration Logicielle (GCL en abrégé) de votre choix, en appliquant un principe simple : 1 fichier par exigence.

PeRKy aide les utilisateurs à garder leur documentation à jour de leurs développements, en s'appuyant sur les mêmes outils que ceux utilisés pour le code. Il intègre également des notions de développement distribué, limitant ainsi hautement les éventuels conflits pouvant survenir lors de la fusion de différentes branches du logiciel.

%prep

%setup -q

%build

#cd src
#. ./stripwav.make
#cd ..

#gzip man/stripwav.1

%install

%{__install} -D -m 755 Src/prk.py                  %{buildroot}%{_bindir}/prk

%clean

rm -Rf $RPM_BUILD_ROOT

%files

%defattr( -, root, root )
%{_bindir}/prk
#%doc doc/*

%changelog
* Sun Jan 12 2014 Guillaume Lemaître <guillaume(+)lemaitre(at)gmail(+)com> - 2014-01-12.0-0
- initial version of the package
