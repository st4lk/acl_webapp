# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.types.compound import ListType, DictType
from base.models import BaseModel


class NewsModel(BaseModel):
    title = StringType()
    content = StringType()
    author = StringType()  # email of author
    comments = ListType(DictType, compound_field=StringType)

    MONGO_COLLECTION = 'news'
