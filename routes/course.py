"""Routes for the course resource.
"""

from run import app
from flask import request, jsonify, abort, make_response
from http import HTTPStatus
import data
import math
from functools import wraps

@app.route("/course/<int:id>", methods=['GET'])
def get_course(id, code=200):
    """Get a course by id.

    :param int id: The record id.
    :return: A single course (see the challenge notes for examples)
    :rtype: object
    """

    """
    -------------------------------------------------------------------------
    Challenge notes:
    -------------------------------------------------------------------------   
    1. Bonus points for not using a linear scan on your data structure.
    """
    # YOUR CODE HERE
    print("IN GET COURSE")
    item = data.Course.query.get(id)
    if item is None:
        msg = f"Course {id} does not exist"
        return jsonify({"data": msg}), 404
        #response = make_response(jsonify(message=msg), 404)
        #abort(response)

    output = data.CourseSchema().dump(item)
    output['date_created'] = output['date_created'].replace("T", " ")
    output['date_updated'] = output['date_created'].replace("T", " ")
    print("AFTER GET COURSE")
    return jsonify({"data":output}), code



@app.route("/course", methods=['GET'])
def get_courses():
    """Get a page of courses, optionally filtered by title words (a list of
    words separated by commas".

    Query parameters: page-number, page-size, title-words
    If not present, we use defaults of page-number=1, page-size=10

    :return: A page of courses (see the challenge notes for examples)
    :rtype: object
    """

    """
    -------------------------------------------------------------------------
    Challenge notes:
    ------------------------------------------------------------------------- 
    1. Bonus points for not using a linear scan, on your data structure, if
       title-words is supplied
    2. Bonus points for returning resulted sorted by the number of words which
       matched, if title-words is supplied.
    3. Bonus points for including performance data on the API, in terms of
       requests/second.
    """
    # YOUR CODE HERE
    page_number = request.args.get('page-number', default=1, type=int)
    page_size = request.args.get('page-size', default=10, type=int)
    title = request.args.get('title-words', type=str)

    if title:
        title_words = title.split(",")
        item = []

        for ttl in title_words:
            search = f"%{ttl}%"
            itm = [data.CourseSchema().dump(customer) for customer in
                   data.Course.query.filter(data.Course.title.like(search))]
            item.extend(itm)

        record_count = len(item)
        page_count = math.ceil(record_count / page_size)

    else:
        record_count = data.Course.query.count()
        page_count = math.ceil(record_count / page_size)

        item = [data.CourseSchema().dump(customer) for customer in
                data.Course.query.paginate(page_number, page_size).items]

    for itm in range(item):
        item[itm]['date_created'] = item[itm]['date_created'].replace("T", " ")
        item[itm]['date_updated'] = item[itm]['date_created'].replace("T", " ")

    return jsonify({'data': item, 'metadata': {"page_count": page_count, "page_number": page_number,
                                               "page_size": page_size, "record_count": record_count}})


# For data validation
def required_params(required):
    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            _json = request.get_json()

            # This is for Create Data requirement
            if required:
                missing = [r for r in required if r not in _json]
                if missing:
                    response = {
                        "status": "error",
                        "message": "Request JSON is missing some required params",
                        "missing": missing
                    }
                    return jsonify(response), 400

            # Validation for description
            if _json['description']:
                if (_json['description'] is not str) and (not (len(_json['description']) < 256)):
                    return jsonify({"message": "Something wrong with description data."}), 400

            # Validation for image_path
            if _json['image_path']:
                if (_json['image_path'] is not str) and (not (len(_json['image_path']) < 100)):
                    return jsonify({"message": "Something wrong with image_path data."}), 400

            # validation for title range
            if _json['title']:
                if len(_json['title']) not in range(5, 101):
                    return jsonify({"message": "Please check length of title."}), 400

            # Validation for price
            if _json['price']:
                if type(_json['price']) not in [float, int]:
                    return jsonify({"message": "Price must be a number."}), 400

            # Validation for discount_price
            if _json['discount_price']:
                if type(_json['discount_price']) not in  [float, int]:
                    return jsonify({"message": "Discount Price must be a number."}), 400

            # Validation for on_discount
            if _json['on_discount']:
                if type(_json['on_discount']) is not bool:
                    return jsonify({'message': "On discount must be boolean."}), 400

            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/course", methods=['POST'])
@required_params(["title", "on_discount", "price"])
def create_course():
    """Create a course.
    :return: The course object (see the challenge notes for examples)
    :rtype: object
    """

    """
    -------------------------------------------------------------------------
    Challenge notes:
    -------------------------------------------------------------------------
    1. Bonus points for validating the POST body fields
    """
    # YOUR CODE HERE
    print("IN CREATE")
    json_data = request.json

    item = data.Course(description=json_data['description'], discount_price=json_data['discount_price'],
                       title=json_data['title'], price =json_data['price'], image_path=json_data['image_path'],
                       on_discount=json_data['on_discount'])

    print("AFTER ADD")
    data.db.session.add(item)
    data.db.session.commit()

    # Now we return the current object
    key_id = item.id
    return get_course(key_id, 201)


@app.route("/course/<int:id>", methods=['PUT'])
@required_params(None)
def update_course(id):
    """Update a a course.
    :param int id: The record id.
    :return: The updated course object (see the challenge notes for examples)
    :rtype: object
    """

    """
    -------------------------------------------------------------------------
    Challenge notes:
    -------------------------------------------------------------------------
    1. Bonus points for validating the PUT body fields, including checking
       against the id in the URL

    """
    # YOUR CODE HERE
    json_data = request.json

    # Validation for id
    if json_data['id']:
        if not json_data['id'] == id:
            return jsonify({"message": "Please check value of id."}), 400

    status = data.db.session.query(data.Course).filter_by(id=id).update(json_data)
    if status:
        data.db.session.commit()
        get_course(id)
    else:
        return jsonify({"message": "Something went wrong."}), 400

@app.route("/course/<int:id>", methods=['DELETE'])
def delete_course(id):
    """Delete a course
    :return: A confirmation message (see the challenge notes for examples)
    """
    """
    -------------------------------------------------------------------------
    Challenge notes:
    -------------------------------------------------------------------------
    None
    """
    # YOUR CODE HERE
    if data.db.session.query(data.Course).filter(data.Course.id==id).delete():
        data.db.session.commit()
        return jsonify({"message": "The specified course was deleted."}), 200
    else:
        message = f"Course {id} does not exist."
        return jsonify({"message": message}), 404
