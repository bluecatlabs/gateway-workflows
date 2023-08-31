# Copyright 2023 BlueCat Networks. All rights reserved.
import configparser
import os
import ipaddress
import math
import re

from IPy import IP
from flask import g

from .exception import InvalidParam
from ..rest_v2.constants import EntityV2


def get_reverse_net_and_name(address_part, subnet):
    result = []
    address_part = address_part.split('.', 4)
    p1 = address_part[0]
    p2 = address_part[1]
    p3 = address_part[2]
    p4 = address_part[3]
    if subnet <= 8:
        reverse_net = '{}.in-addr.arpa'.format(p1)
        name = '{}.{}.{}'.format(p4, p3, p2)
    elif subnet <= 16:
        reverse_net = '{}.{}.in-addr.arpa'.format(p2, p1)
        name = '{}.{}'.format(p4, p3)
    elif subnet <= 24:
        reverse_net = '{}.{}.{}.in-addr.arpa'.format(p3, p2, p1)
        name = p4
    else:
        reverse_net = '{}.{}.{}.{}.in-addr.arpa'.format(p4, p3, p2, p1)
        name = ''

    if divmod(subnet, 8)[1] == 0:
        return [{'reverse_net': reverse_net, 'name': name}]
    zone_number = 128
    number_of_div = 1
    for i in range(1, divmod(subnet, 8)[1]):
        if number_of_div != divmod(subnet, 8)[1]:
            number_of_div += 1
            zone_number = int(zone_number / 2)

    for i in range(zone_number):
        zone_index = int(reverse_net.split('.', 1)[0]) + i
        result.append({'reverse_net': '{}.{}'.format(zone_index, reverse_net.split('.', 1)[1]), 'name': name})
    return result


def get_reverse_net_and_name_ip6(address_part, subnet, is_windows_dns=False):
    bit_left = 128 - subnet
    omit, remainder = divmod(bit_left, 4)
    full_reverse_ptr = ipaddress.IPv6Address(address_part).reverse_pointer
    full_reverse_ptr_splited = full_reverse_ptr.split(".")
    needed_parts = full_reverse_ptr_splited[omit:]
    unneeded_parts = full_reverse_ptr_splited[:omit]
    name = ".".join(unneeded_parts)
    reverse_net = ".".join(needed_parts)
    result = []
    if divmod(subnet, 4)[1] == 0 or is_windows_dns:
        return [{'reverse_net': reverse_net, 'name': name}]
    number_zone = 1 << (4 - divmod(subnet, 4)[1])
    for i in range(number_zone):
        try:
            first_net_name = int(reverse_net[0].lstrip("0x"))
        except ValueError:
            first_net_name = int(reverse_net[0], 16)
        first_net_name = hex(first_net_name + i).lstrip("0x")
        result.append(
            {'reverse_net': '{}.{}'.format(first_net_name if first_net_name else 0, reverse_net[2:]), 'name': name})
    return result


def read_config_file(section, setting_name, default_value='no'):
    config = get_config()
    try:
        data = config[section]
        value = data.get(setting_name, default_value).strip()
    except (configparser.NoSectionError, KeyError):
        value = default_value
    return value


def get_config(config_file_path=''):
    if not config_file_path:
        from .constants import get_default_config
        config_file_path = get_default_config()
    try:
        if not os.path.exists(config_file_path):
            return None
        else:
            config = configparser.ConfigParser()
            config.read(config_file_path)
            return config
    except Exception:
        return None


def get_reverse_zone_name(ip_range):
    try:
        ip_address, subnet = ip_range.split('/')[0], (ip_range.split('/')[1])
        if ':' in ip_address and int(subnet) % 4 != 0:
            ip_address, subnet = ip_range.split('/')[0], ip_range.split('/')[1]
            exploded_ip = ipaddress.IPv6Address(ip_address).exploded.replace(':', '')
            fully_part_count, remainder = divmod(int(subnet), 4)
            reverse_name = ''
            if remainder % 4 != 0:
                remainder_bit = exploded_ip[fully_part_count]
                range_len = 2 ** (4 - remainder)
                reverse_name = f'[{remainder_bit}-{int_to_hexa(hexa_to_int(remainder_bit) + range_len - 1)}]'
                if fully_part_count > 0:
                    reverse_name += '.'
            reverse_name += '.'.join(exploded_ip[:fully_part_count:][::-1])
            reverse_name += '.ip6.arpa'
            return reverse_name
        reverses_name = IP(ip_range).reverseNames()
        reverse_name = reverses_name[0]
        if len(reverses_name) > 1:
            reverse_name = '[' + reverses_name[0].split('.', 1)[0] + '-' + reverses_name[-1].split('.', 1)[
                0] + ']' + '.' + reverses_name[0].split('.', 1)[1]

    except Exception as e:
        g.user.logger.warning(f"Get reverse zone name exception: {e}")
        reverse_name = ''
    return reverse_name


def get_range_hint_from_reverse_zone(reverse_ip_string) -> dict:
    character_split = reverse_ip_string.split('.')
    ip_range_digits = []
    addition_range_str = ''
    if re.search(r'\[([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\-([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4]['
                 r'0-9]|25[0-5])\]', character_split[0]) \
            or re.search(r'\[([0-9a-f]|[0-9A-F])\-([0-9a-f]|[0-9A-F])\]', character_split[0]):
        addition_range_str = character_split[0]
        character_split = character_split[1:]
    for char in character_split:
        if not char.isdigit() and not is_hexa_digit(char):
            break
        ip_range_digits.append(char)
    raw_hint = '.'.join(ip_range_digits)
    ipv4_range_hint = construct_ipv4_hint_from_reverse_digit_list(ip_range_digits, addition_range_str)
    ipv6_range_hint = construct_ipv6_hint_from_reverse_digit_list(ip_range_digits, addition_range_str)
    return {'ipv4_hint': ipv4_range_hint, 'ipv6_hint': ipv6_range_hint, 'raw_hint': raw_hint}


def is_hexa_digit(char):
    if len(char) != 1:
        return False
    return char in 'abcdef' or char in 'ABCDEF' or char.isdigit()


def int_to_hexa(numb: int):
    if numb < 10:
        return str(numb)
    INT_TO_HEXA_DICT = {
        10: 'a',
        11: 'b',
        12: 'c',
        13: 'd',
        14: 'e',
        15: 'f'
    }
    return INT_TO_HEXA_DICT.get(numb, '')


def hexa_to_int(char):
    char = char.lower()
    if char.isdigit() and int(char) < 10:
        return int(char)
    hexa_to_int_dict = {
        'a': 10,
        'b': 11,
        'c': 12,
        'd': 13,
        'e': 14,
        'f': 15
    }
    return hexa_to_int_dict.get(char, -1)


def construct_ipv4_hint_from_reverse_digit_list(ip_range_digits, addition_range=''):
    if (len(ip_range_digits) == 0 and len(addition_range) == 0) or len(ip_range_digits) > 4:
        return ''

    for digit in ip_range_digits:
        if not digit.isdigit() or int(digit) > 255:
            return ''
    ipv4_hint = '.'.join(ip_range_digits[::-1])

    if re.search(r'\[([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\-([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4]['
                 r'0-9]|25[0-5])\]', addition_range):
        addition_range = addition_range.replace('[', '').replace(']', '')
        start_end_ip = addition_range.strip().split('-')
        start_digit = int(start_end_ip[0])
        end_digit = int(start_end_ip[1])
        range_bit = math.log(end_digit - start_digit + 1, 2)
        base_bit_count = len(ip_range_digits) * 8
        if math.floor(range_bit) != range_bit or base_bit_count > 24:
            raise InvalidParam()
        if not ipv4_hint:
            ipv4_hint = str(start_digit)
        else:
            ipv4_hint = ipv4_hint + '.' + str(start_digit)
        leftover = 3 - len(ip_range_digits)
        for _ in range(leftover):
            ipv4_hint += '.0'
    return ipv4_hint


def construct_ipv6_hint_from_reverse_digit_list(ip_range_digits=[], addition_range=''):
    ip_range_digits = ip_range_digits[::-1]
    if (len(ip_range_digits) == 0 and len(addition_range) == 0) or len(ip_range_digits) > 64:
        return ''

    for digit in ip_range_digits:
        if not is_hexa_digit(digit):
            return ''
    if re.search(r'\[([0-9a-f]|[0-9A-F])\-([0-9a-f]|[0-9A-F])\]', addition_range):
        addition_range = addition_range.replace('[', '').replace(']', '')
        start_end_ip = addition_range.strip().split('-')
        start_digit = start_end_ip[0]
        ip_range_digits.append(start_digit)
    is_octet_fulfill = len(ip_range_digits) % 4 == 0

    octets = []
    temp_octet = ''
    for index, char in enumerate(ip_range_digits):
        if (index + 1) % 4 == 0:
            temp_octet += char.upper()
            temp_octet = temp_octet.lstrip('0')
            if not temp_octet:
                temp_octet = '0'
            octets.append(temp_octet)
            temp_octet = ''
        else:
            temp_octet += char.upper()
    if temp_octet:
        octet_origin_len = len(temp_octet)
        temp_octet = temp_octet.lstrip('0')
        if not temp_octet:
            strip_character_count = octet_origin_len - len(temp_octet)
            temp_octet = ''.join(['x' for _ in range(strip_character_count)])
        octets.append(temp_octet)
    ipv6_range = ':'.join(octets).rstrip(":")
    if is_octet_fulfill and len(octets) < 8:
        ipv6_range += ':'
    return ipv6_range


def get_ipv6_reverse_zone(ipv6):
    addr = ipaddress.ip_address(ipv6)
    full_ipv6 = addr.exploded
    ipv6_digit_list = full_ipv6.split(':')
    reverse_zone_chars = []
    for octet in ipv6_digit_list:
        for char in octet:
            reverse_zone_chars.append(char)
    reverse_zone = '.'.join(reverse_zone_chars[::-1])
    return reverse_zone


def get_ipv4_range_from_reverse_zone(reverse_zone):
    character_split = reverse_zone.split('.')
    addition_range_str = ''
    ipv4_range_digits = []
    ipv4_addition_ip = ''
    ipv4_addition_bit_count = 0
    if re.search(r'\[([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\-([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4]['
                 r'0-9]|25[0-5])\]', character_split[0]):
        addition_range_str = character_split[0]
        addition_range = addition_range_str.replace('[', '').replace(']', '')
        start_end_ip = addition_range.strip().split('-')
        ipv4_addition_ip = start_end_ip[0]
        start_digit = int(start_end_ip[0])
        end_digit = int(start_end_ip[1])
        range_bit = math.log(end_digit - start_digit + 1, 2)
        if math.floor(range_bit) != range_bit:
            raise InvalidParam('Invalid addition range')
        ipv4_addition_bit_count = int(range_bit)
        character_split = character_split[1:]
    for char in character_split:
        if not char.isdigit() or int(char) > 255 or int(char) < 0:
            break
        ipv4_range_digits.append(char)
    number_of_ipv4_digit = len(ipv4_range_digits)
    if (number_of_ipv4_digit == 0 and len(ipv4_addition_ip) == 0) or number_of_ipv4_digit > 4:
        raise InvalidParam('Invalid IPv4 range')
    ipv4_range_digits = ipv4_range_digits[::-1]
    if addition_range_str:
        ipv4_range_digits.append(ipv4_addition_ip)
    subnet = 8 * number_of_ipv4_digit
    if ipv4_addition_bit_count > 0:
        subnet += (8 - ipv4_addition_bit_count)
    while len(ipv4_range_digits) < 4:
        ipv4_range_digits.append('0')
    final_ipv4_range = '.'.join(ipv4_range_digits)
    final_ipv4_range += '/{}'.format(subnet)

    return final_ipv4_range


def get_ipv6_range_from_reverse_zone(reverse_zone):
    character_split = reverse_zone.split('.')
    ipv6_range_digits = []
    ipv6_addition_char = ''
    ipv6_addition_bit_count = 0
    if re.search(r'\[([0-9a-f]|[0-9A-F])\-([0-9a-f]|[0-9A-F])\]', character_split[0]):
        addition_range_str = character_split[0]
        addition_range = addition_range_str.replace('[', '').replace(']', '')
        start_end_ip = addition_range.strip().split('-')
        ipv6_addition_char = start_end_ip[0]
        start_digit = hexa_to_int(start_end_ip[0])
        end_digit = hexa_to_int(start_end_ip[1])
        range_bit = math.log(end_digit - start_digit + 1, 2)
        if math.floor(range_bit) != range_bit \
                or not is_hexa_digit(ipv6_addition_char) \
                or not is_hexa_digit(start_end_ip[1]):
            raise InvalidParam('Invalid addition range')
        ipv6_addition_bit_count = int(range_bit)
        character_split = character_split[1:]
    for char in character_split:
        if not is_hexa_digit(char):
            break
        ipv6_range_digits.append(char)
    ipv6_range_digits = ipv6_range_digits[::-1]
    if ipv6_addition_char:
        ipv6_range_digits.append(ipv6_addition_char)
    if len(ipv6_range_digits) == 0 or len(ipv6_range_digits) > 128:
        raise InvalidParam('Invalid IPv6 range')

    octets = []
    temp_octet = ''
    for index, char in enumerate(ipv6_range_digits):
        if (index + 1) % 4 == 0:
            temp_octet += char.upper()
            temp_octet = temp_octet.lstrip('0')
            if not temp_octet:
                temp_octet = '0'
            octets.append(temp_octet)
            temp_octet = ''
        else:
            temp_octet += char.upper()
    if temp_octet:
        octet_origin_len = len(temp_octet)
        temp_octet = temp_octet.lstrip('0')
        if not temp_octet:
            strip_character_count = octet_origin_len - len(temp_octet)
            temp_octet = ''.join(['0' for _ in range(strip_character_count)])
        octets.append(temp_octet)
    final_ipv6_range = ':'.join(octets).rstrip(":")
    if len(octets) < 8:
        final_ipv6_range += '::'
    subnet = len(ipv6_range_digits) * 4 - ipv6_addition_bit_count
    final_ipv6_range += '/{}'.format(subnet)
    return final_ipv6_range


def get_collection_name(collection):
    collection_type = collection.get('type')
    collection_name = collection.get('name')
    if collection_type == EntityV2.ZONE:
        collection_name = collection.get('absoluteName')
    elif collection_type in (EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK,
                             EntityV2.IP4_BLOCK, EntityV2.IP6_BLOCK):
        collection_name = collection.get('range')

    return collection_name
