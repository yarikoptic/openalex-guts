from cached_property import cached_property
import json
import requests
from time import time

from util import elapsed

from app import db


class Unpaywall(object):

    def __init__(self, doi):
        self.doi = doi
        print(f"calling unpaywall api for workaround for now till we get data in postgres")
        start_time = time()
        r = requests.get(f"https://api.unpaywall.org/{doi}?email=team+openalex-postgres-temp@ourresearch.org")
        self.response = r.json()
        print(f"called unpaywall for {doi} took {elapsed(start_time)}")
        super(Unpaywall, self).__init__()

    @cached_property
    def oa_status(self):
        return self.response.get("oa_status", None)

    @cached_property
    def is_paratext(self):
        return self.response.get("is_paratext", None)

    @cached_property
    def best_oa_location_url(self):
        if not self.response:
            return None
        return self.response["best_oa_location"].get("url", None)

    @cached_property
    def best_oa_location_version(self):
        if not self.response:
            return None
        return self.response["best_oa_location"].get("version", None)

    @cached_property
    def best_oa_location_license(self):
        if not self.response:
            return None
        return self.response["best_oa_location"].get("license", None)

    @cached_property
    def oa_locations(self):
        if not self.response:
            return []
        if not self.response.get("oa_locations", None):
            return []
        return self.response.get("oa_locations", None)

    def __repr__(self):
        return "<Unpaywall ( {} ) '{}' {}>".format(self.doi, self.oa_status)



# class Unpaywall(db.Model):
#     __table_args__ = {'schema': 'ins'}
#     __tablename__ = "unpaywall_recordthresher_fields_mv"
#
#     recordthresher_id = db.Column(db.Text, db.ForeignKey("ins.recordthresher_record.id"), primary_key=True)
#     doi = db.Column(db.Text)
#     updated = db.Column(db.DateTime)
#     oa_status = db.Column(db.Text)
#     is_paratext = db.Column(db.Boolean)
#     best_oa_location_url = db.Column(db.Text)
#     best_oa_location_version = db.Column(db.Text)
#     best_oa_location_license = db.Column(db.Text)
#     oa_locations_json = db.Column(db.Text)
#
#     @cached_property
#     def oa_locations(self):
#         if not self.oa_locations_json:
#             return []
#         return json.loads(self.oa_locations_json)
#
#     def __repr__(self):
#         return "<Unpaywall ( {} ) '{}' {}>".format(self.recordthresher_id, self.doi, self.oa_status)




# old

# copy ins.unpaywall_raw from
# 's3://unpaywall-daily-snapshots/unpaywall_snapshot_2021-11-01T083001.jsonl.gz'
# credentials 'CREDS HERE'
# COMPUPDATE ON
# GZIP
# JSON 'auto ignorecase'
# TRUNCATECOLUMNS
# TRIMBLANKS
# region 'us-west-2';

# create or replace view ins.oa_locations_for_unload_view as (
# select doi,
#     replace(replace(replace(replace(oa_locations,
#                  '[{', '{'), '}]', '}'), '},{', '}\n{'),
#                  '"url"',
#                  '"doi": "' || doi || '", "url"'
#                  )
#                  as oa_location_jsonlines
#     from ins.unpaywall_raw
#     where is_oa
#     and doi not like '%\\\\%'
#     and len(oa_locations) < 50000
# ) with no schema binding;
#
# #
# unload ('select oa_location_jsonlines from oa_locations_for_unload_view')
# to 's3://openalex-sandbox/unpaywall/oa_locations.jsonl.gz'
# credentials 'CREDS HERE'
# ALLOWOVERWRITE
# gzip;
#
#
# copy ins.unpaywall_oa_location_raw from 's3://openalex-sandbox/unpaywall/oa_locations.jsonl.gz'
# credentials 'CREDS HERE'
# COMPUPDATE ON
# GZIP
# JSON 'auto ignorecase'
# MAXERROR as 100;
#
#
#
