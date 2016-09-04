'''
Author: <Johnny Hsu, aka. Yu Wei, Hsu>
HW: Homework 10
Date: <04/24/2016>
Homework: ISTA 350 HW10
Section Leader: Will Zielinski 

Description: Web Scraping IV: Fourth part of an introduction to the art of web scraping
'''
import time
import requests, csv
from bs4 import BeautifulSoup
from operator import itemgetter

class Person:
   
    def __init__(self, last, first, ptype, email, phone, unit, position, address, building, room):
        '''
        Description:
        Initialize a Person object.Each Person object has ten instance variables: 
        last (name), first (name), ptype (student, staff, appointed personnel, etc.), 
        email, phone, unit, position, addr, bldg, and rm. 
        Each variable store value from UA's phonebook.
        
        Parameters:
        last: a str that determines the Person's last name 
        first: a str that determines the Person's first name 
        ptype: str that determines the Person's type(student, staff, appointed personnel, etc.), 
        email: a str that determines the Person's email
        phone: a str that determines the Person's phone number
        unit: a str that determines the Person's working unit
        position: a str that determines the Person's position
        address: a str that determines the Person's working address
        building: a str that determines the Person's working building
        room: a str that determines the Person's working room
        
        Return: None
        '''
        self.last = last
        self.first = first
        self.ptype = ptype
        self.email = email
        self.phone = phone
        self.unit = unit
        self.position = position
        self.addr = address
        self.bldg = building
        self.rm = room
        
        
    @classmethod
    def from_soup(cls, soup_person):
        '''
        Description:
        
        This class method to takes a BeautifulSoup object representing an html element with 
        the name span and attribute class="field-content".  
        
        Parameters:
        soup_person: a BeautifulSoup object representing an html element with 
        the name span and attribute class="field-content"
        
        Return: 
        cls: a instance that determines Person
        '''
        name = soup_person.find('h3').get_text().strip().split(',')
        last = name[0].strip()
        first = name[1].strip()
        
        ptype = soup_person.find('span', 'type').get_text().strip()
        email = soup_person.find('a', 'mailto').get_text().strip()
        try:
            phone = soup_person.find('a', 'phoneto').get_text().strip()
        except:
            phone = ''
        try:
            unit = soup_person.find('div', 'degree').get_text().strip()
        except:
            unit = ''
        try:
            position = soup_person.find('div', 'department').get_text().strip().replace('\r', '').split('\n')[0].strip()
        except:
            position = ''
        
        address = ''
        for row in soup_person.find_all('div'):
            content = row.get_text()
            if 'PO Box' in content:
                address = row.get_text().strip()
        
        building = ''
        for row in soup_person.find_all('div'):
            content = row.get_text()
            if 'Building' in content:
                building = content.split(':')[1].strip()
        
        room = ''
        for row in soup_person.find_all('div'):
            content = row.get_text()
            if 'Room' in content:
                room = content.split(':')[1].strip()
        
        return cls(last, first, ptype, email, phone, unit, position, address, building, room)
        
        
    def generator(self):
        '''
        Description:
        This method is to generates the information in self as strings in the order given in 
        init with two exceptions. 
        last and first are in a single string and  bldg and rm are in a single string.
        
        Parameters: None
        
        Return: None
        '''
        yield(self.last +', ' + self.first)
        yield(self.ptype)
        yield(self.email)
        yield(self.phone)
        yield(self.unit)
        yield(self.position)
        yield(self.addr)
        yield(self.bldg + ' rm ' + self.rm)
        
    
    def __repr__(self):
        '''
        Description:
        This method is to returns a string containing first, last, email, and position.
        
        Parameters: None
        
        Return: 
        a str containing first, last, email, and position.
        For example: 'Rocket Thompson, crazy_dog@gmail.com, Happy Dog'. 
        '''
        return self.first + ' ' + self.last + ', ' + self.email + ', ' + self.position  
    
    
    def __eq__(self, other):
        '''
        Description:
        This magic method is to tests equality between two Person objects's email.
        
        Parameters: None
        
        Return: True if self.email == other.email; otherwise, False
        '''
        return self.email == other.email
  
  
    def __lt__(self, other):
        '''
        Description:
        This magic method is to compare two objects. 
        Two objects are equal, return False. 
        If not, base the result on last names. 
        If the last names are equal, base the result on first name
        
        Parameters: None
        
        Return: True if self < other; otherwise, False.
        '''
        if self.email == other.email:
            return False
        else:
            if self.last == other.last:
                return self.first < other.first
            return self.last < other.last
  
  
    def __hash__(self):
        '''
        Description:
        This magic method is to hash calls built-in function hash on email and returns the result. 
        
        Parameters: None
        
        Return: 
        hash(self.email): a int that determines hash value
        '''
        return hash(self.email)
    
   
class People:  
    def __init__(self, person_lst = None, fname = None):
        '''
        Description:
        Initialize the People object. People object has two instance variable: people and missing.
        person holds a list of the Person instances that will go into the output file.
        missing holds the names that were in the input file but not found in the phonebook.
        
        Parameters:
        person_lst: a list that determines a list of person object. Default is None.
        fname: a str that determines the a brunch of names for seaching of UA's phonebook.
        If a fname was passed, the method needs to iterate through the file, 
        reading the input names and searching the UA's phonebook on each one. 
        
        Return: None 
        '''
        if person_lst:
            self.people = person_lst 
        else:
            self.people = []
            
        self.missing = []
        if fname:
            with open(fname) as fp:
                reader = csv.reader(fp)
                for row in reader:
                    last, first = row[0].lower().capitalize(), row[1].lower().capitalize()
                    url = 'http://directory.arizona.edu/phonebook?type_2=&lastname=' + last 
                    url += '&firstname=' + first + '&email=&phone=&attribute_7='
                    soup = BeautifulSoup(requests.get(url).content, 'lxml')
                    soup_people = soup.find_all('span', 'field-content')
                    person_lst = []
                    if soup_people:
                        name_lst= [last, first]
                        for soup_person in soup_people:   
                            person_lst.append(Person.from_soup(soup_person))
                            #self.people.append(Person.from_soup(soup_person))
                        self.select_people(person_lst, name_lst)                   
                    else:
                        self.missing.append([last, first])    
           
         
    def select_people(self, person_lst, name_lst):
        '''
        Description:
        This method is to query the user to determine which of the people 
        in the response the user would like to keep for eventual output.
        
        Parameters:
        person_lst: a list that determines a list of person objects.
        name: a list that determines person's last name and first name
        
        Return: None
        '''
        select_lst = []
        
        if len(person_lst) > 1:
            
            while True:
                self.print_plist(person_lst, name_lst[0], name_lst[1])
                option = input('Enter numbers separated by spaces or return to select all: ')
                option_lst = option.strip().split()
                
                if option_lst == '':
                    self.people.extend(person_lst)
                    break
                elif '0' in option_lst:
                    self.people = []
                    break
                
                try: 
                    option_lst = [int(num) for num in option_lst]
                    for num in option_lst:
                        if num <= len(person_lst):
                            select_lst.append(person_lst[num-1])
                        else:
                            print('Warning: Invalid number ' + str(num) + ' ignored.')
                    self.people.extend(select_lst)
                    break
                except:
                    print('Error: nonnumeric entry detected.  Please choose again.')
        else:
            self.people.extend(person_lst)
            

    @staticmethod
    def print_plist(person_lst, last, first):
        '''
        Description:
        A static method prints the menu for the method select_poeple.
        For example:
            print_plist(self., 'Thompson', 'Richard')
            "********************* Search on Richard Thompson returns: ********************** 
            "  0: Select nobody
            "  1: Richard A Thompson, thompsri@email.arizona.edu, (retired) Associate Profess
            "  2: Richard B Thompson, rbt@math.arizona.edu, (retired) Professor Emeritus
            "  3: Richard Micheal Thompson, richardt1@email.arizona.edu, Undergraduate - Coll
            "  4: Richard Maxwell Thompson, rmthomps@email.arizona.edu, Lecturer, School of I
            "******************************************************************************** 
        
        Parameters:
        person_lst: a list determines a list of Person objects.
        last: a str that determines the Person's last name 
        first: a str that determines the Person's first name 
       
        Return: None
        '''
        print('\n')
        print((' Search on ' + first + ' ' + last + ' returns: ').center(80, '*'))
        print('  0: Select nobody')
        for i, person in enumerate(person_lst):
            output = '  ' + repr(i+1) + ': ' + repr(person) 
            if len(output) <= 80:
                print(output)
            else:
                output = output[0:80]
                print(output)
        
        print('*' * 80)
    

    def write_people(self, fname):
        '''
        Description:
        This method is the point of the generator in Person. If you call 
        generator on a Person object and pass it to the list constructor.
        Write this list into cvs file.
        
        Parameters:
        fname: a str that determines a filename.
        
        Return: None
        '''
        with open(fname, 'w', newline = '') as fw:
            writer = csv.writer(fw)
            for person in self.people:
                writer.writerow(person.generator())
                    
                       
def main():
    '''
    Description:
    1. o
    1. Showe the header and current time: UA Phonebook Search,  day, mm/dd/yyyy, at hh:rr
    For example: *************************  UA Phonebook Search, wednesday, 11/18/2015, at 06:17
    
    2. Create a People object containing a list of person object based on the names.txt and search result.
    3. Elimate duplicates person objects and sort the list, People.people
    4. Write each person in csv file based on search result named people.csv
    5. Show the header and a list of names not found in the UA's phoneboook in order
    For example: ************************* 4 People Not Found *************************
                
    Parameters: None
        
    Return: None
    '''
    
    print('\n')
    print((' UA Phonebook Search, ' + time.strftime('%A, %m/%d/%Y, at %I:%M') + ' ').center(80, '*'))
    people = People(fname="names.txt") 
    people.people = list(set(people.people))
    people.people = sorted(people.people)
    people.write_people('people.csv')
    
    print('\n')
    print( (' ' + repr(len(people.missing)) + ' People Not Found ').center(80, '*'))
    for name in sorted(people.missing, key=itemgetter(0,1)):
        print('  ' + name[1].lower().capitalize() + ' ' + name[0].lower().capitalize())
    print()
    
    
if __name__ == '__main__':
    main()