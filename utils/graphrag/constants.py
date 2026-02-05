# Params:
# $limit     : INTEGER  optional cap on returned nodes (e.g. 200)
QUERY_TEMPLATE = """
WITH node AS seed, score
WITH collect(seed) AS seeds
OPTIONAL MATCH (seed)-[]-(a:sop) WHERE seed IN seeds
WITH seeds, collect(DISTINCT a) AS A
OPTIONAL MATCH (seed)-[]-(c:rp_claim) WHERE seed IN seeds
WITH seeds, A, collect(DISTINCT c) AS C
WITH seeds, A, C,
     CASE
       WHEN size(A) > 0 THEN 'sop'
       WHEN size(C) > 0 THEN 'rp_claim'
       ELSE NULL
     END AS chosen
WITH
  CASE chosen
    WHEN 'sop' THEN A
    WHEN 'rp_claim' THEN C
    ELSE []
  END AS firstHops,
  chosen
WHERE size(firstHops) > 0
UNWIND firstHops AS h1
MATCH p=(h1)-[*1..2]-(n)
RETURN DISTINCT n AS node, chosen AS chosen_first_hop_label
LIMIT coalesce($limit, 100);
"""

DEFAULT_PROMPT="Hi, I am facing above average fatigue levels recently. Can you help me with some recommendations to manage my fatigue?"

PROMPT_TEMPLATE = (
    "You are a knowledgeable and friendly assistant to provide concise and tailored support and recommendations to aviation ground crews that are facing fatigue issues.\n"
    "There are 2 types of documents provided as context, which can be checked in the document_type property of each content:\n"
    "1. Internal Documents(document_type = \"sop\"): These are documents from the company's internal knowledge base. They contain information on the Standard Operating Procedures\n"
    "of the company regarding mental health practices.\n"
    "2. Literature Documents(document_type = \"rp\"): These are documents from external sources, such as research papers, articles, and books, that provide additional context and information on mental health practices.\n"
    "You are provided with their roster information, summarised sleep information, and exercise information.\n"
    "Your job is to address the user query based on documents provided, taking into account their summarised sleep and exercise and roster information, using a warm and empathetic tone. **BE AS CONCISE AS POSSIBLE**\n"
    "DO NOT make assumptions about ANY personal details.\n"
    "Prioritise information from Internal Documents over Literature Documents when answering queries.\n"
    "Be explicit about the source of the information is from when answering queries from the source property from the document context, mentioning whether it is from SOP or Research Literature, but **DO NOT** quote document_types when constructing the answer.\n"
)

PROMPT_TEMPLATE += """
Roster Information:
{roster_info}

Exercise Information:
{exercise_info}

Sleep Information:
{sleep_info}

Document Context:
{context}

Query: 
{query_text}
Answer:
"""


# DEPRECATED - use backend/models/data.py PERSONNELS_DATA instead
# Mock user info dictionary for demo purposes
USER_INFO_DICTIONARY = {
    1: {
        "position": "Air Traffic Controller",
        "age": 28,
        "gender": "F",
        "roster_info": {

        },
        # "roster_info": {
        #     "past_flights_7_days": [
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "London Heathrow",
        #             "Arrairport": "New York JFK",
        #             "Actstartdatetimeutc": "2025-09-13T06:00:00Z",
        #             "Actenddatetimeutc": "2025-09-13T12:00:00Z"
        #         },
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "New York JFK",
        #             "Arrairport": "Toronto Pearson",
        #             "Actstartdatetimeutc": "2025-09-14T10:00:00Z",
        #             "Actenddatetimeutc": "2025-09-14T12:00:00Z"
        #         },
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "Toronto Pearson",
        #             "Arrairport": "London Heathrow",
        #             "Actstartdatetimeutc": "2025-09-15T08:00:00Z",
        #             "Actenddatetimeutc": "2025-09-15T14:00:00Z"
        #         },
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "London Heathrow",
        #             "Arrairport": "Dubai",
        #             "Actstartdatetimeutc": "2025-09-17T05:00:00Z",
        #             "Actenddatetimeutc": "2025-09-17T13:00:00Z"
        #         },
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "Dubai",
        #             "Arrairport": "Singapore",
        #             "Actstartdatetimeutc": "2025-09-19T09:00:00Z",
        #             "Actenddatetimeutc": "2025-09-19T17:00:00Z"
        #         }
        #     ]
        # },
        "current_location": "Singapore",
        "favourite_activities": ["running", "photography", "travel blogging"]
    },
    2: {
        "position": "Air Traffic Controller",
        "age": 31,
        "gender": "M",
        # "roster_info": {
        #     "past_flights_7_days": [
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "Tokyo Narita",
        #             "Arrairport": "Sydney",
        #             "Actstartdatetimeutc": "2025-09-14T23:00:00Z",
        #             "Actenddatetimeutc": "2025-09-15T08:00:00Z"
        #         },
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "Sydney",
        #             "Arrairport": "Bangkok",
        #             "Actstartdatetimeutc": "2025-09-17T01:00:00Z",
        #             "Actenddatetimeutc": "2025-09-17T08:00:00Z"
        #         },
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "Bangkok",
        #             "Arrairport": "Tokyo Narita",
        #             "Actstartdatetimeutc": "2025-09-19T06:00:00Z",
        #             "Actenddatetimeutc": "2025-09-19T14:00:00Z"
        #         }
        #     ]
        # },
        "current_location": "Tokyo",
        "favourite_activities": ["surfing", "guitar", "cycling"]
    },
    3: {
        "position": "Air Traffic Controller",
        "age": 26,
        "gender": "F",
        # "roster_info": {
        #     "past_flights_7_days": [
        #         {
        #             "Assignmentclass": "FLY",
        #             "Depairport": "Paris Charles de Gaulle",
        #             "Arrairport": "Doha",
        #             "Actstartdatetimeutc": "2025-09-18T09:00:00Z",
        #             "Actenddatetimeutc": "2025-09-18T15:00:00Z"
        #         }
        #     ]
        # },
        "current_location": "Doha",
        "favourite_activities": ["painting", "baking", "yoga"]
    }
}
