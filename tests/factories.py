# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
from datetime import date

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Recommendation, Type


class RecommendationFactory(factory.Factory):
    """Creates fake recommendations that you use to test"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendation

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    user_id = factory.Sequence(lambda n: n)
    user_segment = factory.Faker('sentence', nb_words=4)
    viewed_in_last7d = FuzzyChoice(choices=[True, False])
    bought_in_last30d = FuzzyChoice(choices=[True, False])
    last_relevance_date = FuzzyDate(date(2008, 1, 1))
    recommendation_type = FuzzyChoice(choices=[
        Type.SIMILAR_PRODUCT, Type.RECOMMENDED_FOR_YOU, Type.UPGRADE,
        Type.FREQ_BOUGHT_TOGETHER, Type.ADD_ON, Type.TRENDING,
        Type.TOP_RATED, Type.NEW_ARRIVAL, Type.UNKNOWN])
    