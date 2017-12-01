'''
generic: 
    text: Generic Device

linux:
    text: Linux

os_category = {}
'''
#categories = {'generic': 'Generic Device', 'linux': 'Linux', 'vmware': 'VMware', 'qnap': 'QNAP TurboNAS', 'dss': 'Open-E DSS', \
#              'vyatta': 'Vyatta Core', 'vyos': 'VyOS','endian': 'Endian', 'openwrt': 'OpenWrt', \
#              'ddwrt': 'DD-WRT' }
categories = [
  {
    "default": "null"
  },
  {
    "generic": "Generic Device"
  },
  {
    "linux": "Linux"
  },
  {
    "vmware": "VMware"
  },
  {
    "qnap": "QNAP TurboNAS"
  },
  {
    "dss": "Open-E DSS"
  },
  {
    "vyatta": "Vyatta Core"
  },
  {
    "vyos": "VyOS"
  },
  {
    "endian": "Endian"
  },
  {
    "openwrt": "OpenWrt"
  },
  {
    "ddwrt": "DD-WRT"
  },
  {
    "wut": "Web-Thermograph"
  },
  {
    "terastation": "BUFFALO TeraStation"
  },
  {
    "cumulus-os": "Cumulus Linux"
  },
  {
    "nimble-os": "Nimble Storage"
  },
  {
    "firebrick": "Firebrick"
  },
  {
    "fireeye": "Fireeye"
  },
  {
    "ipso": "Check Point IPSO"
  },
  {
    "sofaware": "Check Point Embedded NGX"
  },
  {
    "infoblox": "Infoblox"
  },
  {
    "splat": "Check Point SecurePlatform"
  },
  {
    "gaia": "Check Point GAiA"
  },
  {
    "infratec-rms": "Infratec RMS"
  },
  {
    "sensatronics": "Sensatronics"
  },
  {
    "ibmi": "IBM System i"
  },
  {
    "freebsd": "FreeBSD"
  },
  {
    "openbsd": "OpenBSD"
  },
  {
    "netbsd": "NetBSD"
  },
  {
    "dragonfly": "DragonflyBSD"
  },
  {
    "netware": "Novell Netware"
  },
  {
    "darwin": "Mac OS X"
  },
  {
    "monowall": "m0n0wall"
  },
  {
    "pfsense": "pfSense"
  },
  {
    "freenas": "FreeNAS"
  },
  {
    "nas4free": "NAS4Free"
  },
  {
    "solaris": "Sun Solaris"
  },
  {
    "opensolaris": "Sun OpenSolaris"
  },
  {
    "openindiana": "OpenIndiana"
  },
  {
    "nexenta": "NexentaOS"
  },
  {
    "sun-ilom": "Sun ILOM"
  },
  {
    "nestos": "Nexsan NST"
  },
  {
    "datadomain": "DD OS"
  },
  {
    "aix": "AIX"
  },
  {
    "alteon-ad": "Alteon Application Director"
  },
  {
    "adva": "Adva Optical"
  },
  {
    "adva-fsp150": "Adva Optical"
  },
  {
    "equallogic": "Storage Array Firmware"
  },
  {
    "compellent": "Storage Center"
  },
  {
    "adtran-aos": "ADTRAN AOS"
  },
  {
    "aos": "Alcatel-Lucent OS"
  },
  {
    "omnistack": "Alcatel-Lucent Omnistack"
  },
  {
    "aosw": "Alcatel-Lucent AOS-W"
  },
  {
    "timos": "Alcatel-Lucent TimOS"
  },
  {
    "bdcom-ios": "BDCOM"
  },
  {
    "billion": "Billion"
  },
  {
    "bridgewave": "BridgeWave"
  },
  {
    "casa-dcts": "CASA DCTS"
  },
  {
    "iosxr": "Cisco IOS-XR"
  },
  {
    "iosxe": "Cisco IOS-XE"
  },
  {
    "ios": "Cisco IOS"
  },
  {
    "acsw": "Cisco ACE"
  },
  {
    "asa": "Cisco ASA"
  },
  {
    "fwsm": "Cisco Firewall Service Module"
  },
  {
    "pixos": "Cisco PIX-OS"
  },
  {
    "nxos": "Cisco NX-OS"
  },
  {
    "sanos": "Cisco SAN-OS"
  },
  {
    "catos": "Cisco CatOS"
  },
  {
    "cisco-prime": "Cisco Prime"
  },
  {
    "wlc": "Cisco WLC"
  },
  {
    "cisco-ons": "Cisco Cerent ONS"
  },
  {
    "cisco-acs": "Cisco Secure ACS"
  },
  {
    "cisco-lms": "Cisco Prime LMS"
  },
  {
    "cisco-ise": "Cisco Identity Services Engine"
  },
  {
    "cisco-ade": "Cisco ADE"
  },
  {
    "cisco-acns": "Cisco ACNS"
  },
  {
    "cisco-tp": "Cisco TelePresence"
  },
  {
    "cisco-uc": "Cisco Unified Communications"
  },
  {
    "cisco-acano": "Cisco Acano"
  },
  {
    "cisco-altiga": "Cisco VPN Concentrator"
  },
  {
    "meraki": "Cisco Meraki"
  },
  {
    "cimc": "Cisco Integrated Management Controller"
  },
  {
    "asyncos": "Cisco IronPort"
  },
  {
    "ciscoscos": "Cisco Service Control Engine"
  },
  {
    "cisco-spa": "Cisco SPA"
  },
  {
    "ciscosb": "Cisco Small Business"
  },
  {
    "ciscosb-rv": "Cisco (Linksys) Router"
  },
  {
    "ciscosb-wl": "Cisco (Linksys) Wireless"
  },
  {
    "ciscosb-nss": "Cisco SB Storage"
  },
  {
    "cyan": "Cyan"
  },
  {
    "liberator": "Fastback Wireless"
  },
  {
    "vrp": "Huawei VRP"
  },
  {
    "huawei-vsp": "Huawei VSP"
  },
  {
    "huawei-ias": "Huawei IAS"
  },
  {
    "huawei-vp": "Huawei ViewPoint"
  },
  {
    "huawei-ism": "Huawei Storage"
  },
  {
    "huawei-wl": "Huawei Wireless"
  },
  {
    "huawei-imana": "Huawei iMana"
  },
  {
    "zxr10": "ZTE ZXR10"
  },
  {
    "zxa10": "ZTE ZXA10"
  },
  {
    "zxv10": "ZTE ZXV10"
  },
  {
    "zxip10": "ZTE ZXIP10"
  },
  {
    "netgear": "Netgear"
  },
  {
    "netgear-readyos": "Netgear ReadyData OS"
  },
  {
    "netgear-readynas": "Netgear ReadyNAS"
  },
  {
    "nimbra": "Net Insight Nimbra"
  },
  {
    "korenix-jetnet": "Korenix Jetnet"
  },
  {
    "supermicro-switch": "Supermicro Switch"
  },
  {
    "junos": "Juniper JunOS"
  },
  {
    "junose": "Juniper JunOSe"
  },
  {
    "jwos": "Juniper JWOS"
  },
  {
    "screenos": "Juniper ScreenOS"
  },
  {
    "juniperive": "Juniper IVE"
  },
  {
    "eltex-switch": "Eltex Switch"
  },
  {
    "fortigate": "Fortinet Fortigate"
  },
  {
    "fortiswitch": "Fortinet FortiSwitch"
  },
  {
    "fortivoice": "Fortinet FortiVoice"
  },
  {
    "forti-os": "Fortinet OS"
  },
  {
    "bti7000": "BTI 7000"
  },
  {
    "ciena": "SAOS"
  },
  {
    "dasan-nos": "DASAN"
  },
  {
    "routeros": "Mikrotik RouterOS"
  },
  {
    "mikrotik-swos": "Mikrotik SwOS"
  },
  {
    "ironware": "Brocade FastIron/IronWare"
  },
  {
    "ironware-ap": "Brocade AP"
  },
  {
    "fabos": "Brocade FabricOS"
  },
  {
    "nos": "Brocade NOS"
  },
  {
    "xos": "Extreme XOS"
  },
  {
    "extremeware": "Extremeware"
  },
  {
    "extreme-wlc": "Extreme Wireless Controller"
  },
  {
    "enterasys": "Enterasys"
  },
  {
    "enterasys-wl": "Extreme Wireless Controller"
  },
  {
    "eltek": "Eltek"
  },
  {
    "atto-storage": "ATTO Storage"
  },
  {
    "maipu-mypower": "Maipu MyPower"
  },
  {
    "gcom": "GCOM"
  },
  {
    "bluecat-adonis": "BlueCat Adonis"
  },
  {
    "bcmc": "Blue Coat Management Center"
  },
  {
    "cas": "Blue Coat Content Analysis System"
  },
  {
    "packetshaper": "Blue Coat Packetshaper"
  },
  {
    "proxyav": "Blue Coat Proxy AV"
  },
  {
    "proxysg": "Blue Coat SGOS"
  },
  {
    "zhonedslam": "Zhone DLSAM"
  },
  {
    "zhone-znid": "Zhone ZNID"
  },
  {
    "zhone-ethx": "Zhone EtherXtend"
  },
  {
    "zhone-mxk": "Zhone MXK"
  },
  {
    "zhone-malc": "Zhone MALC"
  },
  {
    "a10-ax": "A10 ACOS"
  },
  {
    "avaya-ers": "ERS Software"
  },
  {
    "avaya-bsr": "BSR Software"
  },
  {
    "avaya-wl": "Avaya Wireless"
  },
  {
    "avaya-phone": "Avaya IP Phone"
  },
  {
    "avaya-server": "Avaya Server"
  },
  {
    "nortel-baystack": "Baystack Software"
  },
  {
    "arista_eos": "Arista EOS"
  },
  {
    "calix": "Calix"
  },
  {
    "calix-blc": "Calix BLC"
  },
  {
    "netscaler": "Citrix Netscaler"
  },
  {
    "f5": "F5 BIG-IP"
  },
  {
    "airconsole": "Air Console"
  },
  {
    "sitemonitor": "PacketFlux SiteMonitor"
  },
  {
    "hiveos": "HiveOS"
  },
  {
    "canopy": "Cambium Canopy"
  },
  {
    "cambium-ptp": "Cambium PTP"
  },
  {
    "epmp": "Cambium ePMP"
  },
  {
    "proxim": "Proxim"
  },
  {
    "raisecom": "Raisecom"
  },
  {
    "ruckus-zf": "Ruckus ZoneFlex"
  },
  {
    "ruckus-zd": "Ruckus ZoneDirector"
  },
  {
    "ruckus-scg": "Ruckus SmartCellGateway"
  },
  {
    "ruckus-sz": "Ruckus SmartZone"
  },
  {
    "ruckus-wl": "Ruckus Wireless"
  },
  {
    "trango-apex": "Trango Apex"
  },
  {
    "ftos": "Dell/Force10 NOS"
  },
  {
    "dnos6": "Dell Networking OS"
  },
  {
    "powerconnect-fastpath": "Dell PowerConnect (FastPath)"
  },
  {
    "powerconnect-radlan": "Dell PowerConnect (RADLAN)"
  },
  {
    "powervault": "Dell PowerVault"
  },
  {
    "drac": "Dell iDRAC"
  },
  {
    "sonicwall": "SonicOS"
  },
  {
    "sonicwall-ssl": "SonicOS SSL"
  },
  {
    "arbos": "ArbOS"
  },
  {
    "broadcom_fastpath": "Broadcom (FastPath)"
  },
  {
    "quanta-switch": "Quanta Switch"
  },
  {
    "plos": "PacketLogic"
  },
  {
    "mlnx-os": "MLNX-OS"
  },
  {
    "netopia": "Motorola Netopia"
  },
  {
    "tranzeo": "Tranzeo"
  },
  {
    "exalt": "Exalt"
  },
  {
    "breeze": "Alvarion Breeze"
  },
  {
    "breezemax": "Alvarion BreezeMax"
  },
  {
    "dlinkap": "D-Link Access Point"
  },
  {
    "dlinkvoip": "D-Link VoIP Gateway"
  },
  {
    "dlinkdpr": "D-Link Print Server"
  },
  {
    "dlink": "D-Link Switch"
  },
  {
    "dlink-ios": "D-Link Router"
  },
  {
    "dlink-generic": "D-Link Device"
  },
  {
    "dlink-dsl": "D-Link DSL"
  },
  {
    "dlink-nas": "D-Link Storage"
  },
  {
    "dlink-mc": "D-Link MediaConverter"
  },
  {
    "dlinkfw": "D-Link Firewall"
  },
  {
    "moxa-np6000": "Moxa NP6000"
  },
  {
    "moxa-np5000": "Moxa NP5000"
  },
  {
    "tplinkap": "TP-LINK Access Point"
  },
  {
    "tplink": "TP-LINK Switch"
  },
  {
    "tplink-adsl": "TP-LINK ADSL"
  },
  {
    "innacomm": "Innacomm Router"
  },
  {
    "axiscam": "AXIS Network Camera"
  },
  {
    "axisencoder": "AXIS Network Video Encoder"
  },
  {
    "axisdocserver": "AXIS Network Document Server"
  },
  {
    "axisprintserver": "AXIS Network Print Server"
  },
  {
    "hikvision-cam": "Hikvision Network Camera"
  },
  {
    "hikvision-dvr": "Hikvision DVR"
  },
  {
    "gta-gb": "GTA GB-OS"
  },
  {
    "eppc-ups": "EPPC"
  },
  {
    "ge-ups": "General Electric UPS"
  },
  {
    "gamatronicups": "Gamatronic UPS Stack"
  },
  {
    "powerware": "Powerware UPS"
  },
  {
    "eaton-sc": "Eaton SC"
  },
  {
    "eaton-epdu": "Eaton ePDU"
  },
  {
    "mgeups": "Eaton (MGE) UPS"
  },
  {
    "mgepdu": "Eaton (MGE) PDU"
  },
  {
    "deltaups": "Delta UPS"
  },
  {
    "janitza": "Janitza Electronics"
  },
  {
    "liebert": "Liebert"
  },
  {
    "avocent": "Avocent"
  },
  {
    "cyclades": "Cyclades"
  },
  {
    "aten": "Aten"
  },
  {
    "aten-pdu": "Aten PDU"
  },
  {
    "rittalcmc3_lcp": "Rittal CMC-III-LCP"
  },
  {
    "rittalcmc3_pu": "Rittal CMC-III-PU"
  },
  {
    "rittalcmc_pu": "Rittal CMC-PU"
  },
  {
    "rittalcmc_lcp": "Rittal CMC-LCP"
  },
  {
    "teracom": "Teracom TCW"
  },
  {
    "engenius": "EnGenius Access Point"
  },
  {
    "engenius-switch": "EnGenius Managed Switch"
  },
  {
    "airport": "Apple AirPort"
  },
  {
    "windows": "Microsoft Windows"
  },
  {
    "ibmnos": "IBM NOS"
  },
  {
    "ibm-tape": "IBM Tape Library"
  },
  {
    "ibm-flexswitch": "IBM Flex Switch"
  },
  {
    "ibm-imm": "Lenovo IMM"
  },
  {
    "ibm-infoprint": "IBM Infoprint"
  },
  {
    "onefs": "Isilon OneFS"
  },
  {
    "netapp": "NetApp"
  },
  {
    "ddn": "DataDirect Networks"
  },
  {
    "arris-d5": "Arris D5"
  },
  {
    "arris-c3": "Arris C3"
  },
  {
    "procurve": "HP ProCurve"
  },
  {
    "procurve-ap": "HP ProCurve Access Point"
  },
  {
    "hpuww": "HP Unified Wired-WLAN Appliance"
  },
  {
    "hpvc": "HP Virtual Connect"
  },
  {
    "hpux": "HP-UX"
  },
  {
    "hp-proliant": "HP ProLiant"
  },
  {
    "hpstorage": "HP StorageWorks"
  },
  {
    "hpmsm": "HP Colubris"
  },
  {
    "hpilo": "HP iLO Management"
  },
  {
    "hpoa": "HP Onboard Administrator"
  },
  {
    "hpups": "HP UPS OS"
  },
  {
    "3com": "3Com OS"
  },
  {
    "h3c": "H3C Comware"
  },
  {
    "hh3c": "HP Comware"
  },
  {
    "speedtouch": "Thomson Speedtouch"
  },
  {
    "zywall": "ZyXEL ZyWALL"
  },
  {
    "prestige": "ZyXEL Prestige"
  },
  {
    "zyxeles": "ZyXEL Ethernet Switch"
  },
  {
    "zyxelnwa": "ZyXEL NWA"
  },
  {
    "ies": "ZyXEL DSLAM"
  },
  {
    "allied": "AlliedWare"
  },
  {
    "alliedwareplus": "AlliedWare Plus"
  },
  {
    "allied-radlan": "Allied Telesis (RADLAN)"
  },
  {
    "actelis": "Actelis"
  },
  {
    "microsens": "Microsens"
  },
  {
    "microsens-g6": "Microsens G6"
  },
  {
    "apc": "APC OS"
  },
  {
    "racktivity": "Racktivity EnergySwitch"
  },
  {
    "interseptor": "Jacarta InterSeptor"
  },
  {
    "oec": "OEC PDU"
  },
  {
    "netbotz": "APC Netbotz"
  },
  {
    "pcoweb": "Carel pCOWeb"
  },
  {
    "ccpower": "C&C Power"
  },
  {
    "saf-ipradio": "SAF"
  },
  {
    "netvision": "Socomec Net Vision"
  },
  {
    "baytech-pdu": "Baytech PDU"
  },
  {
    "areca": "Areca RAID Subsystem"
  },
  {
    "netmanplus": "NetMan Plus"
  },
  {
    "generex-ups": "Generex UPS Adapter"
  },
  {
    "sensorgateway": "ServerRoom Sensor Gateway"
  },
  {
    "sensorprobe": "AKCP SensorProbe"
  },
  {
    "securityprobe": "AKCP securityProbe"
  },
  {
    "servsensor": "BlackBox ServSensor"
  },
  {
    "minkelsrms": "Minkels RMS"
  },
  {
    "roomalert": "AVTECH RoomAlert"
  },
  {
    "ipoman": "Ingrasys iPoMan"
  },
  {
    "wxgoos": "ITWatchDogs Goose"
  },
  {
    "papouch": "Papouch Probe"
  },
  {
    "cometsystem-p85xx": "Comet System P85xx"
  },
  {
    "dell-laser": "Dell Laser"
  },
  {
    "efi-fiery": "EFI Print Controller"
  },
  {
    "ricoh": "Ricoh Printer"
  },
  {
    "lexmark": "Lexmark Printer"
  },
  {
    "lg-printer": "LG Printer"
  },
  {
    "sindoh": "SINDOH Printer"
  },
  {
    "nrg": "NRG Printer"
  },
  {
    "epson-printer": "Epson Printer"
  },
  {
    "xerox-printer": "Xerox Printer"
  },
  {
    "fuji-xerox-printer": "Fuji Xerox Printer"
  },
  {
    "samsung-printer": "Samsung Printer"
  },
  {
    "canon-printer": "Canon Printer"
  },
  {
    "jetdirect": "HP Printer"
  },
  {
    "olivetti-printer": "Olivetti Printer"
  },
  {
    "sharp-printer": "Sharp Printer"
  },
  {
    "okilan": "OKI Printer"
  },
  {
    "brother-printer": "Brother Printer"
  },
  {
    "konica-printer": "Konica-Minolta Printer/Copier"
  },
  {
    "develop": "Develop Printer"
  },
  {
    "kyocera": "Kyocera Printer"
  },
  {
    "estudio": "Toshiba Printer"
  },
  {
    "panasonic-printer": "Panasonic Printer"
  },
  {
    "sentry3": "ServerTech Sentry3"
  },
  {
    "sentry-pdu": "ServerTech Sentry PDU"
  },
  {
    "gude-epc": "Gude Expert Power Control"
  },
  {
    "gude-pdu": "Gude Expert PDU"
  },
  {
    "geist-pdu": "Geist PDU"
  },
  {
    "geist-watchdog": "Geist Watchdog"
  },
  {
    "geist-climate": "Geist Environmental"
  },
  {
    "raritan": "Raritan PDU"
  },
  {
    "raritan-kvm": "Raritan KVM"
  },
  {
    "raritan-emx": "Raritan EMX"
  },
  {
    "mrvld": "MRV LambdaDriver"
  },
  {
    "mrvos": "MRV Optiswitch"
  },
  {
    "mrvnbs": "MRV"
  },
  {
    "poweralert": "Tripp Lite PowerAlert"
  },
  {
    "tl-mgmt": "Tripp Lite Management"
  },
  {
    "jdsu_edfa": "JDSU OEM Erbium Dotted Fibre Amplifier"
  },
  {
    "symbol": "Symbol AP"
  },
  {
    "firebox": "WatchGuard Fireware"
  },
  {
    "panos": "PanOS"
  },
  {
    "arubaos": "ArubaOS"
  },
  {
    "aruba-meshos": "MeshOS"
  },
  {
    "trapeze": "Juniper Wireless"
  },
  {
    "lcos": "LCOS"
  },
  {
    "lancom-l54-dual": "LCOS (L-54 Dual)"
  },
  {
    "lancom-l310": "LCOS (L-310)"
  },
  {
    "lancom-c54g": "LCOS (C-54g)"
  },
  {
    "lancom-3550": "LCOS (3550)"
  },
  {
    "lancom-3850": "LCOS (3850)"
  },
  {
    "dsm": "Synology DSM"
  },
  {
    "srm": "Synology SRM"
  },
  {
    "ceragon": "Ceragon FibeAir"
  },
  {
    "cts-switch": "CTS Switch"
  },
  {
    "cts-wl": "CTS Switch"
  },
  {
    "digios": "Digi OS"
  },
  {
    "digi-anyusb": "Digi AnywhereUSB"
  },
  {
    "tsl-mdu12": "TSL MDU12"
  },
  {
    "unifi": "Ubiquiti UniFi Wireless"
  },
  {
    "unifi-switch": "Ubiquiti UniFi Switch"
  },
  {
    "airos": "Ubiquiti AirOS"
  },
  {
    "edgeos": "Ubiquiti EdgeOS"
  },
  {
    "edgemax": "Ubiquiti EdgeMAX"
  },
  {
    "airos-af": "Ubiquiti AirFiber"
  },
  {
    "draytek": "Draytek"
  },
  {
    "seos": "SmartEdge OS"
  },
  {
    "barracudangfw": "Barracuda NG Firewall"
  },
  {
    "barracuda-sc": "Barracuda Security"
  },
  {
    "barracuda-lb": "Barracuda LB"
  },
  {
    "audiocodes": "Audiocodes"
  },
  {
    "shoretelos": "ShoreTel OS"
  },
  {
    "mcd": "Mitel Controller"
  },
  {
    "acme": "Acme Packet"
  },
  {
    "poseidon": "Poseidon"
  },
  {
    "hwg-ste": "HWg-STE"
  },
  {
    "hwg-pwr": "HWg-PWR"
  },
  {
    "teradici-pcoip": "PCoIP"
  },
  {
    "iqnos": "Infinera IQ"
  },
  {
    "picos": "Pica8 OS"
  },
  {
    "radware": "Radware DefensePro"
  },
  {
    "wipg": "WePresent WiPG"
  },
  {
    "smartware": "Patton Smartnode"
  },
  {
    "steelhead": "Riverbed Steelhead"
  },
  {
    "opengear": "Opengear"
  },
  {
    "zeustm": "Riverbed Stingray"
  },
  {
    "smartos": "SmartOS"
  },
  {
    "fiberroad-mc": "FiberRoad Media Converter"
  },
  {
    "clavister-cos": "Clavister cOS"
  },
  {
    "oneos": "OneAccess OneOS"
  },
  {
    "sophos": "Sophos UTM"
  },
  {
    "uniping": "UniPing"
  },
  {
    "uniping-server-v3": "UniPing Server"
  },
  {
    "uniping-server": "UniPing Server"
  },
  {
    "netping-pwr3": "NetPing 8/PWRv3/SMS"
  },
  {
    "bintec-os": "BinTec OS"
  },
  {
    "bintec-voip": "BinTec VoIP"
  },
  {
    "acdos": "Accedian Networks"
  },
  {
    "mimosa-backhaul": "Mimosa Backhaul Radio"
  },
  {
    "jetnexus-lb": "jetNexus LB"
  },
  {
    "aethra-dsl": "Aethra DSL"
  },
  {
    "atosnt": "Aethra ATOS-NT"
  },
  {
    "aethra-vcs": "Aethra VCS"
  },
  {
    "iskratel-fb": "Iskratel Fiberblade"
  },
  {
    "iskratel-linux": "Iskratel Server"
  },
  {
    "mcafee-meg": "McAfee MEG Appliance"
  },
  {
    "plugandtrack": "Plug&Track v2"
  },
  {
    "edgecore-os": "Edgecore OS"
  }
]

def formatOSCategories():
    os_category = {}
    return categories



#print formatOSCategories()



