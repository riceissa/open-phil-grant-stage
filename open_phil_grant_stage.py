#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import re
import requests
import mysql.connector
from bs4 import BeautifulSoup

def main():
    cnx = mysql.connector.connect(user='issa', database='donations')
    cursor = cnx.cursor()

    # Map from grant URL to grant stage; this is where we will store all
    # results
    grant_stage_map = {}

    print(grant_stage_guess(grant_stage_map, cursor,
                            "https://www.openphilanthropy.org/focus/global-catastrophic-risks/potential-risks-advanced-artificial-intelligence/stanford-university-percy-liang-planning-grant",
                            "Stanford University",
                            "2018-02-01"))

    cursor.close()
    cnx.close()


def grant_stage_guess(grant_stage_map, cursor, grant_url, grantee, donation_date):
    """Return one of "planning grant", "initial grant", "renewal grant", "exit
    grant", or "repeated grant"."""
    if grant_url in grant_stage_map:
        # We already have the grant stage for this grant, so do nothing and
        # return
        return None

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
    print(type(earliest_grant_date))

    if soup.body.find_all(text=re.compile("renewal grant")):
        return "renewal grant"
    if soup.body.find_all(text=re.compile("a renewal")):
        return "renewal grant"
    if soup.body.find_all(text=re.compile("exit grant")):
        return "exit grant"

    planning_pat1 = re.compile(r"planning grant", re.IGNORECASE)
    planning_pat2 = re.compile(r"previously.*planning grant", re.IGNORECASE)
    if planning_pat1.findall(doc) and not planning_pat2.findall(doc):
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
    # of all earlier grants; if there is at least one initial grant, then this
    # is a repeated grant. Otherwise, it is an initial grant.
    for d, u in date_url_pairs:
        if d < donation_date and grant_stage_map[u] == "initial grant":
            return "repeated grant"
    return "initial grant"


if __name__ == "__main__":
    main()
