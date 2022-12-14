import pynetbox
from os import environ

nb = pynetbox.api(
    environ.get("NETBOX_URL"),
    token=environ.get("NETBOX_TOKEN")
)


def get_next_available_ip(prefix_id):
    return nb.ipam.prefixes.get(prefix_id).available_ips.list()[0]


def get_interfaces_with_tag(tag):
    return nb.dcim.interfaces.filter(tag=tag)


def get_addresses_for_interface(id):
    return nb.ipam.ip_addresses.filter(interface_id=id)


def assign_ip_to_interface(ip, interface):
    return nb.ipam.ip_addresses.create(address=ip.address, assigned_object_type="dcim.interface",
                                       assigned_object_id=interface.id,
                                       description=f"[auto-dhcp] {interface.device.name} ({interface.name})")


def dhcp_reservation_line(mac, ip, hostname):
    return f"dhcp-host={mac},{hostname},{ip.address.split('/')[0]},12h"


def main():
    INTERFACES_TAG = "dhcp_range_1"
    PREFIX_ID = 1
    for interface in get_interfaces_with_tag(INTERFACES_TAG):
        if interface.count_ipaddresses > 0:
            # interface has already an IP address assigned
            ip = next(get_addresses_for_interface(interface.id))
            ip.tags = [{"name": INTERFACES_TAG, "slug": INTERFACES_TAG}]
            ip.save()
        else:
            # Find an available IP address
            ip = get_next_available_ip(PREFIX_ID)
            ip_object = assign_ip_to_interface(ip, interface)
            ip_object.tags = [{"name": INTERFACES_TAG, "slug": INTERFACES_TAG}]
            ip_object.save()
        print(dhcp_reservation_line(interface.mac_address, ip, interface.device.name))


if __name__ == '__main__':
    main()
