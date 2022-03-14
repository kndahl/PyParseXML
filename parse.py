# etree -------------------------------------------------------------
from xml.etree import cElementTree as ElementTree
from timeit import default_timer as timer

class ListConfig(list):
    def __init__(self, aList):

        for element in aList:

            # Getting attributes
            attrib = element.attrib
            if len(attrib) > 0:
                self.append(attrib)

            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(DictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(ListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    d = {'$':text}
                    self.append(d)


class DictConfig(dict):
    def __init__(self, parent_element):

        childrenNames = [child.tag for child in parent_element.iter()]

        if parent_element.items(): #attributes
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                #print len(element), element[0].tag, element[1].tag
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = DictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: ListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))

                if childrenNames.count(element.tag) > 1:
                    try:
                        currentValue = self[element.tag]
                        currentValue.append(aDict)
                        self.update({element.tag: currentValue})
                    except: #the first of its kind, an empty list must be created
                        self.update({element.tag: [aDict]}) #aDict is written in [], i.e. it will be a list
                else:
                    self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

def parse_etree(xml_string):
    root = ElementTree.XML(xml_string)
    xmldict = DictConfig(root)
    return(xmldict)
