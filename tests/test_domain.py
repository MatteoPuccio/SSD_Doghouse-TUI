import builtins
import datetime
import json
from datetime import date
from pathlib import Path
from unittest import mock
from unittest.mock import patch, Mock, PropertyMock, mock_open

import pytest
import requests
from requests import Response
from valid8 import ValidationError

import freezegun
import doghousetui
from doghousetui import Utils
from doghousetui.domain import Dogname, Date, Breed, Sex, Dog_description, Estimated_adult_size, PictureUrl


@pytest.fixture
def valid_dog_names():
    return ["Dogname", "Dname", "Do", "Mrdog", "Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]

def test_valid_DogName(valid_dog_names):
    for i in valid_dog_names:
        Dogname(i)

def test_dog_name_must_contains_at_least_two_chars():
    with pytest.raises(ValidationError):
        Dogname("D")

def test_dog_name_must_contains_at_most_50_chars():
    with pytest.raises(ValidationError):
        Dogname("Dooooooooooooooooooooooooooooooooooooooooooooogname")

def test_dog_name_reject_not_letters_characters():
    Dogname("Dogname")
    for i in ["Dogname#","Dog\tname" ,"Dogname@", "Dog?name", " Dog name" , "Dog.name", "Dogname2"]:
        with pytest.raises(ValidationError):
            Dogname(i)

def test_dog_name_must_start_with_upper_letters():
    Dogname("Dogname")
    with pytest.raises(ValidationError):
        Dogname("dogname")

def test_dog_name_has_lower_letter_after_first_character():
    Dogname("Dogname")
    for i in ["DGgname", "DogName@", "DognAme" ,"DOgname"]:
        with pytest.raises(ValidationError):
            Dogname(i)

def test_date_must_be_before_or_at_most_today():
    with freezegun.freeze_time("2000-1-1"):
        Date(datetime.date.today())
        for i in [date(2016, 4, 30), date(2000, 2, 26), date(2000, 12, 1)]:
            with pytest.raises(ValidationError):
                Date(i)

def test_date_to_string_print_date_in_format_Y_M_D():
    with freezegun.freeze_time("2020-1-1"):
        dates = [date(2016, 4, 30), date(2000, 2, 26), date(2000, 12, 1)]
        string_dates = ["2016-04-30", "2000-02-26", "2000-12-01"]
        for i in range(0, 3):
            assert str(Date(dates[i])) == string_dates[i]


def test_sex_can_be_M_or_F_only():
    Sex("M")
    Sex("F")
    for i in ["m","Male","female","f","1","0"]:
        with pytest.raises(ValidationError):
            Sex(i)

def test_sex_equality():
    sexes = ["M", "F"]
    for i in range(2):
        for j in range(2):
                assert (Sex(sexes[i]) == Sex(sexes[j])) == (i == j)
        assert Sex(sexes[i]) != object()

def test_value_obtained():
    sexes = ["M", "F"]
    for i in range(2):
        assert Sex(sexes[i]).value == sexes[i]

def test_description_must_contains_at_most_400_char():
    with pytest.raises(ValidationError):
        Dog_description("a" * 401)


def test_description_rejects_invalid_content():
    for i in ["a@aaa", "aaaaaa#aaaaa", "AAdasdbb'"]:
        with pytest.raises(ValidationError):
            Dog_description(i)

def test_estimated_adult_size_must_contains_only_valid_sizes():
    for i in ["XXL", "22", "aaaa","","s","l","m"]:
        with pytest.raises(ValidationError):
            Estimated_adult_size(i)


def test_dog_breeds_correctly_read_the_file_and_return_the_correct_dog_breeds():
    pass

def test_read_breed_correctly_read_the_file():
    with mock.patch('builtins.open', mock_open(read_data='{"dogs": \n["Bolognese", "Stockfish", "Dogfish"]}\n')):
        for i in ["Bolognese", "Stockfish", "Dogfish"]:
            assert i in Breed.read_breeds()

def test_read_breed_path_exists_and_can_be_opened():
    with mock.patch.object(json, "load") as mock_load:
        mock_load.return_value = {"dogs": ["Bolognese", "Stockfish", "Dogfish"]}
        Breed("Bolognese")

def test_dog_breeds_must_belongs_to_default_breeds():
    with mock.patch.object(doghousetui.domain.Breed, "read_breeds") as mock_read_breeds:
        mock_read_breeds.return_value = frozenset(["Bolognese", "Stockfish", "Dogfish"])
        Breed("Bolognese")
        with pytest.raises(ValidationError):
            Breed("Not in the default breeds")

def test_pictureurl_can_be_empty_or_correct_url():
    for i in ["", "https://imgur.com/6755v", "https://imgur.com/Ada6755nsv"]:
        PictureUrl(i)

def test_pictureurl_cannot_be_a_not_valid_url():
    for i in ["aaahttps://imgur.com/6755vaaa", "http://imgur.com/6755v", "https://google.com/Ada6755nsv"]:
        with pytest.raises(ValidationError):
            PictureUrl(i)