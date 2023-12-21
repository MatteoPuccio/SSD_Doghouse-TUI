import builtins
import datetime
import json
from datetime import date
from pathlib import Path
from unittest import mock
from unittest.mock import patch, Mock, PropertyMock, mock_open, MagicMock

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




class TestDogName:

    @pytest.fixture
    def valid_dog_names(self):
        return ["", "Dogname", "Dname", "Do", "Mrdog", "Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
    def test_valid_DogName(self, valid_dog_names):
        for i in valid_dog_names:
            Dogname(i)

    def test_dog_name_by_default_is_empty(self):
        assert Dogname().value == ""

    def test_dog_name_must_contains_at_most_50_chars(self):
        with pytest.raises(ValidationError):
            Dogname("Dooooooooooooooooooooooooooooooooooooooooooooogname")

    def test_dog_name_reject_not_letters_characters(self):
        Dogname("Dogname")
        for i in ["Dogname#","Dog\tname" ,"Dogname@", "Dog?name", " Dog name" , "Dog.name", "Dogname2"]:
            with pytest.raises(ValidationError):
                Dogname(i)

    def test_dog_name_must_start_with_upper_letters(self):
        Dogname("Dogname")
        with pytest.raises(ValidationError):
            Dogname("dogname")

    def test_dog_name_has_lower_letter_after_first_character(self):
        Dogname("Dogname")
        for i in ["DGgname", "DogName@", "DognAme" ,"DOgname"]:
            with pytest.raises(ValidationError):
                Dogname(i)

class TestDate:
    def test_date_must_be_before_or_at_most_today(self):
        with freezegun.freeze_time("2000-1-1"):
            Date(datetime.date.today())
            for i in [date(2016, 4, 30), date(2000, 2, 26), date(2000, 12, 1)]:
                with pytest.raises(ValidationError):
                    Date(i)

    def test_date_to_string_print_date_in_format_Y_M_D(self):
        with freezegun.freeze_time("2020-1-1"):
            dates = [date(2016, 4, 30), date(2000, 2, 26), date(2000, 12, 1)]
            string_dates = ["2016-04-30", "2000-02-26", "2000-12-01"]
            for i in range(0, 3):
                assert str(Date(dates[i])) == string_dates[i]

    def test_date_return_correctly_the_years_elapsed_until_today(self):
        with freezegun.freeze_time("2020-10-10"):
            dates = [date(2016, 4, 30), date(2000, 10, 11), date(2020, 10, 10)]
            years = [4, 19 , 0]
            for i in range(0, 3):
                assert Date(dates[i]).calculate_years_to_today() == years[i]

    def test_date_return_the_days_elapsed(self):
        with freezegun.freeze_time("2023-12-15"):
            dates = [date(2020, 4, 30), date(2019, 12, 16), date(2023, 12, 15)]
            years = [1324, 1460, 0]
            for i in range(0, 3):
                assert Date(date.today()).days_elapsed(Date(dates[i])) == years[i]

    @pytest.mark.parametrize("test_input", ["-2020-02-26-19", "-2020-02-26","2020-13-30", "2020-01-34"])
    def test_date_parse_must_not_not_Y_M_D_strings(self, test_input):
        with pytest.raises(DateWrongFormatError):
            Date.parse_date(test_input)

class TestSex:
    def test_sex_can_be_M_or_F_only(self):
        Sex("M")
        Sex("F")
        for i in ["m","Male","female","f","1","0"]:
            with pytest.raises(ValidationError):
                Sex(i)

    def test_sex_equality(self):
        sexes = ["M", "F"]
        for i in range(2):
            for j in range(2):
                    assert (Sex(sexes[i]) == Sex(sexes[j])) == (i == j)
            assert Sex(sexes[i]) != object()

    def test_value_obtained(self):
        sexes = ["M", "F"]
        for i in range(2):
            assert Sex(sexes[i]).value == sexes[i]

class TestDogDescription:
    def test_description_must_contains_at_most_400_char(self):
        with pytest.raises(ValidationError):
            DogDescription("a" * 401)


    def test_description_rejects_invalid_content(self):
        for i in ["a@aaa", "aaaaaa#aaaaa", "AAdasdbb'"]:
            with pytest.raises(ValidationError):
                DogDescription(i)

class TestEstimatedAdultSize:
    def test_estimated_adult_size_must_contains_only_valid_sizes(self):
        for i in ["XXL", "22", "aaaa","","s","l","m"]:
            with pytest.raises(ValidationError):
                EstimatedAdultSize(i)

class TestBreed:
    def test_read_breed_correctly_read_the_file(self):
        with mock.patch('builtins.open', mock_open(read_data='{"dogs": \n["Bolognese", "Stockfish", "Dogfish"]}\n')):
            for i in ["Bolognese", "Stockfish", "Dogfish"]:
                assert i in Breed.read_breeds()


    def test_dog_breeds_must_belongs_to_default_breeds(self):
        with mock.patch.object(doghousetui.domain.Breed,"breeds", frozenset(["Bolognese", "Stockfish", "Dogfish"])):
            Breed("Stockfish")
            with pytest.raises(ValidationError):
                Breed("Not in the default breeds")

    @pytest.mark.parametrize("breeds", [
        (["Half-breeded", "Stockfish", "Mockfish","Dogfish"], ["Dogfish", "Mockfish", "Stockfish"] , "fish" )
        , (["Tolpin", "Colin", "Rolpin","Volpi"],["Volpi", "Tolpin", "Rolpin",],"Volpin")
        , (["Cihuahua", "Cimiao", "cimiahua","cimiahua"], ["Cihuahua", "cimiahua" , "Scimiahua"], "Cihuahua")])
    def test_most_similar_breeds_must_return_top_3_most_similar_breeds(self, breeds):
        with mock.patch.object(doghousetui.domain.Breed, "breeds", frozenset(breeds[0]) ):
            most_similar:list = Breed.similar_breeds(breeds[2])
            assert most_similar.sort() == breeds[1].sort()
    def test_most_similar_breeds_must_return_the_exact_one_as_first_if_present(self):
        with mock.patch.object(doghousetui.domain.Breed, "breeds", frozenset(["Cihuahua", "Cimiao", "Scimiahua","cimiahua"])):
            most_similar:list = Breed.similar_breeds("Cihuahua")
            assert most_similar[0] == "Cihuahua"

    def test_most_similar_breeds_must_return_all_if_not_enough_breeds(self):
        with mock.patch.object(doghousetui.domain.Breed, "breeds", frozenset(["Cihuahua", "Cimiao"])):
            most_similar:list = Breed.similar_breeds("Cihuahua")
            assert most_similar == ["Cihuahua", "Cimiao"]

    def test_most_similar_breeds_must_return_valid_breeds(self):
        with mock.patch.object(doghousetui.domain.Breed, "breeds", frozenset(["Cihuahua", "Cimiao", "Scimiahua","cimiahua"])):
            most_similar:list = Breed.similar_breeds("Cihuahua")
            for i in most_similar:
                Breed(i)


    def test_most_similar_breeds_must_return_valid_breeds_with_empty_string(self):
        with mock.patch.object(doghousetui.domain.Breed, "breeds", frozenset(["Cihuahua", "Cimiao", "Scimiahua","cimiahua"])):
            most_similar:list = Breed.similar_breeds("")
            for i in most_similar:
                Breed(i)

class TestPictureUrl:
    def test_pictureurl_can_be_empty_or_correct_url(self):
        for i in ["", "https://i.imgur.com/6755v.jpeg", "https://i.imgur.com/Ada6755nsv.png"]:
            PictureUrl(i)

    def test_pictureurl_cannot_be_a_not_valid_url(self):
        for i in ["aaahttps://i.imgur.com/6755vaaa", "https://i.imgur.com/6755v", "https://google.com/Ada6755nsv"]:
            with pytest.raises(ValidationError):
                PictureUrl(i)

class TestId:
    def test_id_cannot_be_negative(self):
        DogId(0)
        for i in range(1,10):
            DogId(i)
            with pytest.raises(ValidationError):
                DogId(-i)

class TestDog:

    @pytest.fixture
    def valid_DogId(self):
        return DogId(1)

    @pytest.fixture
    def valid_Dogname(self):
        return Dogname("Pippo")

    @pytest.fixture
    def valid_DogDescription(self):
        return DogDescription("description")

    @pytest.fixture
    def valid_DogBirthInfo(self):
        return DogBirthInfo(Breed("Bolognese"),Sex("M"),Date.parse_date("2020-05-05"),EstimatedAdultSize("L"))


    @pytest.fixture
    def valid_entry_date(self):
        return Date.parse_date("2020-05-05")


    @pytest.fixture
    def valid_DogPicture(self):
        return PictureUrl("https://i.imgur.com/Ada6755nsv.png")

    @pytest.fixture
    def valid_dogBuilder(self,valid_DogId, valid_DogBirthInfo, valid_entry_date):
        return Dog.Builder(valid_DogId,valid_DogBirthInfo, valid_entry_date, True)


    @pytest.mark.parametrize("today", [("2022-05-06",2 ), ("2021-05-05", 1),("2023-10-10",3 ), ("2020-05-05",0), ("2021-05-04",0)])
    def test_dog_birth_info_return_correct_age(self, valid_DogBirthInfo, today):
        with freezegun.freeze_time(today[0]):
            assert valid_DogBirthInfo.age() == today[1]


    def test_dog_builder_cannot_create_dog_with_entry_after_birth_date(self,valid_DogId, valid_DogBirthInfo):
        entry_date = date.fromisoformat(str(valid_DogBirthInfo.birth_date)) + datetime.timedelta(days=-1)
        dog_builder = Dog.Builder(valid_DogId,valid_DogBirthInfo, Date(entry_date), True)
        with pytest.raises(ValidationError):
            dog_builder.build()


    def test_dog_builder_add_dog_description_create_valid_dog(self,valid_dogBuilder,valid_DogDescription):
       valid_dogBuilder.with_description(valid_DogDescription).build()

    def test_dog_had_description_return_true_if_dog_has_description(self,valid_dogBuilder, valid_DogDescription):
       dog:Dog = valid_dogBuilder.with_description(valid_DogDescription).build()
       assert dog.has_description()

    def test_dog_has_name_return_true_if_dog_has_not_default_name(self,valid_dogBuilder, valid_Dogname):
       dog:Dog = valid_dogBuilder.with_dogname(valid_Dogname).build()
       assert dog.has_name()

    def test_dog_has_name_return_true_if_dog_has_not_default_name(self,valid_dogBuilder, valid_Dogname):
       dog:Dog = valid_dogBuilder.build()
       assert dog.has_name() == False

    def test_dog_had_description_return_false_if_dog_has_not_a_description(self, valid_dogBuilder):
       dog:Dog = valid_dogBuilder.build()
       assert dog.has_description() == False

    def test_dog_has_picture_return_true_if_dog_has_not_default_url_picture(self, valid_dogBuilder, valid_DogPicture):
       dog:Dog = valid_dogBuilder.with_picture(valid_DogPicture).build()
       assert dog.has_picture()

    def test_dog_has_picture_return_false_if_dog_has_default_url_picture(self, valid_dogBuilder):
       dog:Dog = valid_dogBuilder.build()
       assert dog.has_picture() == False
    def test_dog_builder_add_dog_name_create_valid_dog(self, valid_dogBuilder, valid_Dogname):
        valid_dogBuilder.with_dogname(valid_Dogname).build()

    def test_dog_builder_add_dog_picture_create_valid_dog(self, valid_dogBuilder, valid_DogPicture):
        valid_dogBuilder.with_picture(valid_DogPicture).build()

    def test_dog_builder_cannot_call_two_times_build(self, valid_DogId, valid_DogBirthInfo, valid_entry_date):
        dog_builder = Dog.Builder(valid_DogId,valid_DogBirthInfo, valid_entry_date, True)
        dog_builder.build()
        with pytest.raises(ValidationError):
            dog_builder.build()


    def test_dog_cannot_be_created_with_constructor(self, valid_DogId, valid_DogBirthInfo, valid_entry_date):
        with pytest.raises(ValidationError):
            Dog(valid_DogId, valid_DogBirthInfo, valid_entry_date, True, object())
















