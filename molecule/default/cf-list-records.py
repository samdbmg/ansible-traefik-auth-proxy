#!/usr/bin/env python3

import argparse
import logging

import cloudflare

logging.basicConfig()
logger = logging.getLogger("cf-list-dns")
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search a Cloudflare DNS zone for records matching a term, return a list of matches")

    parser.add_argument("zone", help="Name of DNS zone to search")
    parser.add_argument("search", help="Term to search for")
    parser.add_argument("--strip-domain", "-s", help="Strip the base domain from results", action="store_true")

    args = parser.parse_args()

    cf = cloudflare.Cloudflare()
    # query for the zone name and expect only one value back
    try:
        zone = None
        for z in cf.zones.list(name=args.zone, per_page=1):
            zone = z
            break
    except cloudflare.APIError as e:
        exit('/zones.get %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))

    if zone is None:
        exit('No zones found')
    
    # extract the zone_id which is needed to process that zone
    zone_id = zone.id
    logger.info(f"Looking up records matching {args.search} in {zone_id}")

    # request the DNS records from that zone
    try:
        for record in cf.dns.records.list(zone_id=zone_id, search=args.search):
            name = record.name

            if not args.search in name:
                # Eliminate false positives picked up by search
                continue

            if args.strip_domain:
                name = name.replace(args.zone, "").rstrip('.')

            print(name)
    except cloudflare.APIError as e:
        exit('/zones/dns_records.get %d %s - api call failed' % (e, e))

    logger.info("Done")    
