from __future__ import unicode_literals
import boto
import sure  # noqa
import requests

from moto import mock_dynamodb
from moto.dynamodb import dynamodb_backend

from boto.exception import DynamoDBResponseError


@mock_dynamodb
def test_list_tables():
    name = 'TestTable'
    dynamodb_backend.create_table(name, hash_key_attr="name", hash_key_type="S")
    conn = boto.connect_dynamodb('the_key', 'the_secret')
    assert conn.list_tables() == ['TestTable']


@mock_dynamodb
def test_list_tables_layer_1():
    dynamodb_backend.create_table("test_1", hash_key_attr="name", hash_key_type="S")
    dynamodb_backend.create_table("test_2", hash_key_attr="name", hash_key_type="S")
    conn = boto.connect_dynamodb('the_key', 'the_secret')
    res = conn.layer1.list_tables(limit=1)
    expected = {"TableNames": ["test_1"], "LastEvaluatedTableName": "test_1"}
    res.should.equal(expected)

    res = conn.layer1.list_tables(limit=1, start_table="test_1")
    expected = {"TableNames": ["test_2"]}
    res.should.equal(expected)


@mock_dynamodb
def test_describe_missing_table():
    conn = boto.connect_dynamodb('the_key', 'the_secret')
    conn.describe_table.when.called_with('messages').should.throw(DynamoDBResponseError)


@mock_dynamodb
def test_sts_handler():
    res = requests.post("https://sts.amazonaws.com/", data={"GetSessionToken": ""})
    res.ok.should.be.ok
    res.text.should.contain("SecretAccessKey")


@mock_dynamodb
def test_dynamodb_with_connect_to_region():
    # this will work if connected with boto.connect_dynamodb()
    dynamodb = boto.dynamodb.connect_to_region('us-west-2')

    schema = dynamodb.create_schema('column1', str(), 'column2', int())
    dynamodb.create_table('table1', schema, 200, 200)
