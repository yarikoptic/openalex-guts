import datetime

from sqlalchemy.dialects.postgresql import JSONB

from app import db, FIELDS_INDEX
from bulk_actions import create_bulk_actions
import models


class Field(db.Model):
    __table_args__ = {'schema': 'mid'}
    __tablename__ = "field"

    field_id = db.Column(db.Integer, db.ForeignKey("mid.topic.field_id"), primary_key=True)
    display_name = db.Column(db.Text)
    display_name_alternatives = db.Column(JSONB)
    description = db.Column(db.Text)
    wikidata_url = db.Column(db.Text)
    wikipedia_url = db.Column(db.Text)
    json_entity_hash = db.Column(db.Text)
    updated_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime)

    def domain(self):
        domain_query = (
            db.session.query(models.Domain)
            .join(models.Topic, models.Domain.domain_id == models.Topic.domain_id)
            .filter(models.Topic.field_id == self.field_id)
            .first()
        )
        return domain_query.to_dict(return_level="minimum")

    @property
    def id(self):
        return self.field_id

    def subfields(self):
        subfields_query = (
            db.session.query(models.Subfield)
            .join(models.Topic, models.Subfield.subfield_id == models.Topic.subfield_id)
            .filter(models.Topic.field_id == self.field_id)
            .all()
        )
        subfields_list = [subfield.to_dict(return_level="minimum") for subfield in subfields_query]
        subfield_list_sorted = sorted(subfields_list, key=lambda x: x['display_name'].lower())
        return subfield_list_sorted

    def store(self):
        bulk_actions, new_entity_hash = create_bulk_actions(self, FIELDS_INDEX)
        self.json_entity_hash = new_entity_hash
        return bulk_actions

    def to_dict(self, return_level="full"):
        response = {'id': self.field_id,
                    'display_name': self.display_name}
        if return_level == "full":
            response.update({
                "description": self.description,
                "display_name_alternatives": self.display_name_alternatives,
                "ids": {
                    "wikidata": self.wikidata_url,
                    "wikipedia": self.wikipedia_url
                },
                "works_count": int(self.counts.paper_count or 0) if self.counts else 0,
                "cited_by_count": int(self.counts.citation_count or 0) if self.counts else 0,
                "domain": self.domain(),
                "subfields": self.subfields(),
                "works_api_url": f"https://api.openalex.org/works?filter=topics.field.id:{self.field_id}",
                "updated_date": datetime.datetime.utcnow().isoformat(),
                "created_date": self.created_date.isoformat()[0:10] if isinstance(self.created_date, datetime.datetime) else self.created_date[0:10]
            })
        return response

    def __repr__(self):
        return "<Field ( {} ) {}>".format(self.field_id, self.display_name)
