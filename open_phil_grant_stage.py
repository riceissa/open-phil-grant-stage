#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import sys
import re
import requests
import mysql.connector
import csv
from bs4 import BeautifulSoup

def main():
    cnx = mysql.connector.connect(user='issa', database='donations')
    cursor = cnx.cursor()

    # Map from grant URL to grant stage; this is where we will store all
    # results
    grant_stage_map = {}

    cursor.execute("""select donee,donation_date,url
                      from donations
                      where donor = 'Open Philanthropy Project'
                      order by donation_date""")
    donation_triples = cursor.fetchall()

    fieldnames = ["grant_url", "grant_stage"]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for (grantee, donation_date, grant_url) in donation_triples:
        grant_stage = grant_stage_guess(grant_stage_map, cursor, grant_url,
                                        grantee, donation_date)
        writer.writerow({"grant_url": grant_url, "grant_stage": grant_stage})
        grant_stage_map[grant_url] = grant_stage

    cursor.close()
    cnx.close()


def grant_stage_guess(grant_stage_map, cursor, grant_url, grantee, donation_date):
    """Return one of "planning grant", "initial grant", "renewal grant", "exit
    grant", or "repeated grant"."""
    response = requests.get(grant_url)
    soup = BeautifulSoup(response.content, "lxml")

    # Remove all "aside" tags because these sometimes contain the titles of
    # other grants, e.g.
    # https://www.openphilanthropy.org/focus/global-catastrophic-risks/potential-risks-advanced-artificial-intelligence/stanford-university-support-percy-liang
    for tag in soup.find_all("aside"):
        tag.decompose()

    doc = soup.get_text()

    cursor.execute("""select donation_date,url
                      from donations
                      where donor = 'Open Philanthropy Project' and
                            donee = %s""",
                   (grantee,))
    date_url_pairs = cursor.fetchall()
    earliest_grant_date = min(x[0] for x in date_url_pairs)

    if soup.body.find_all(text=re.compile("renewal grant")):
        return "renewal grant"
    if soup.body.find_all(text=re.compile("a renewal")):
        return "renewal grant"

    pat1 = re.compile(r"exit grant", re.IGNORECASE)
    pat2 = re.compile(r"previously[^.]*exit grant", re.IGNORECASE)
    if pat1.findall(doc) and not pat2.findall(doc):
        return "exit grant"

    pat1 = re.compile(r"planning grant", re.IGNORECASE)
    pat2 = re.compile(r"previously[^.]*planning grant", re.IGNORECASE)
    if pat1.findall(doc) and not pat2.findall(doc):
        return "planning grant"

    if len(date_url_pairs) == 1:
        # There is only one grant to this grantee, and we haven't returned yet
        # so it can't be a planning grant. That means it must be an initial
        # grant.
        return "initial grant"

    if donation_date == earliest_grant_date:
        # This is the earliest grant to this grantee, and it's not a planning
        # grant, so it must be an initial grant.
        return "initial grant"

    # Now things get interesting. This grant is not the earliest, it's not a
    # planning grant, it's not a renewal grant, and it's not an exit grant. It
    # could either be an initial grant (say, if the earlier grants were just
    # planning grants) or a repeated grant (if there was an earlier initial
    # grant). The only way to tell the grant stage is to check the grant stages
    # of all earlier grants (that's precisely why we started looping through
    # the grants in chronological order); if there is at least one initial
    # grant, then this is a repeated grant. Otherwise, it is an initial grant.
    for d, u in date_url_pairs:
        if d < donation_date and grant_stage_map[u] == "initial grant":
            return "repeated grant"
    return "initial grant"


if __name__ == "__main__":
    main()
