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
from doghousetui.Exception import DateWrongFormatError
from doghousetui.domain import Dogname, Date, Breed, Sex, DogDescription, EstimatedAdultSize, PictureUrl, DogId, \
    DogBirthInfo, Dog


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

def test_date_return_correctly_the_years_elapsed_until_today():
    with freezegun.freeze_time("2020-10-10"):
        dates = [date(2016, 4, 30), date(2000, 10, 11), date(2020, 10, 10)]
        years = [4, 19 , 0]
        for i in range(0, 3):
            assert Date(dates[i]).calculate_years_to_today() == years[i]

def test_date_return_the_days_elapsed():
    with freezegun.freeze_time("2023-12-15"):
        dates = [date(2020, 4, 30), date(2019, 12, 16), date(2023, 12, 15)]
        years = [1324, 1460, 0]
        for i in range(0, 3):
            assert Date(date.today()).days_elapsed(Date(dates[i])) == years[i]

@pytest.mark.parametrize("test_input", ["-2020-02-26-19", "-2020-02-26","2020-13-30", "2020-01-34"])
def test_date_parse_must_not_not_Y_M_D_strings(test_input):
    with pytest.raises(DateWrongFormatError):
        Date.parse_date(test_input)

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
        DogDescription("a" * 401)


def test_description_rejects_invalid_content():
    for i in ["a@aaa", "aaaaaa#aaaaa", "AAdasdbb'"]:
        with pytest.raises(ValidationError):
            DogDescription(i)

def test_estimated_adult_size_must_contains_only_valid_sizes():
    for i in ["XXL", "22", "aaaa","","s","l","m"]:
        with pytest.raises(ValidationError):
            EstimatedAdultSize(i)

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

def test_id_cannot_be_negative():
    DogId(0)
    for i in range(1,10):
        DogId(i)
        with pytest.raises(ValidationError):
            DogId(-i)


@pytest.fixture
def valid_DogId():
    return DogId(1)


@pytest.fixture
def valid_DogDescription():
    return DogDescription("description")

@pytest.fixture
def valid_DogBirthInfo():
    return DogBirthInfo.create("Pippo","Bolognese","M","2020-05-05")


@pytest.fixture
def valid_entry_date():
    return Date.parse_date("2020-05-05")


@pytest.fixture
def valid_DogPicture():
    return PictureUrl()

@pytest.fixture
def valid_EstimatedAdultSize():
    return EstimatedAdultSize("M")

@pytest.fixture
def valid_dogBuilder(valid_DogId, valid_DogBirthInfo, valid_entry_date):
    return Dog.Builder(valid_DogId,valid_DogBirthInfo, valid_entry_date, True)


@pytest.mark.parametrize("today", [("2022-05-06",2 ), ("2021-05-05", 1),("2023-10-10",3 ), ("2020-05-05",0), ("2021-05-04",0)])
def test_dog_birth_info_return_correct_age(valid_DogBirthInfo, today):
    with freezegun.freeze_time(today[0]):
        assert valid_DogBirthInfo.age() == today[1]


def test_dog_builder_cannot_create_dog_with_entry_after_birth_date(valid_DogId, valid_DogBirthInfo):
    entry_date = date.fromisoformat(str(valid_DogBirthInfo.birth_date)) + datetime.timedelta(days=-1)
    dog_builder = Dog.Builder(valid_DogId,valid_DogBirthInfo, Date(entry_date), True)
    with pytest.raises(ValidationError):
        dog_builder.build()


def test_dog_builder_add_dog_description_create_valid_dog(valid_dogBuilder,valid_DogDescription):
   valid_dogBuilder.with_description(valid_DogDescription).build()

def test_dog_builder_add_dog_estimated_size_create_valid_dog(valid_dogBuilder, valid_EstimatedAdultSize):
    valid_dogBuilder.with_estimated_adult_size(valid_EstimatedAdultSize).build()

def test_dog_builder_add_dog_picture_create_valid_dog(valid_dogBuilder, valid_DogPicture):
    valid_dogBuilder.with_picture(valid_DogPicture).build()

def test_dog_builder_cannot_call_two_times_build(valid_DogId, valid_DogBirthInfo, valid_entry_date):
    dog_builder = Dog.Builder(valid_DogId,valid_DogBirthInfo, valid_entry_date, True)
    dog_builder.build()
    with pytest.raises(ValidationError):
        dog_builder.build()


def test_dog_cannot_be_created_with_constructor(valid_DogId, valid_DogBirthInfo, valid_entry_date):
    with pytest.raises(ValidationError):
        Dog(valid_DogId, valid_DogBirthInfo, valid_entry_date, True, object())
















