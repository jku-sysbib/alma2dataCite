import xml.etree.ElementTree as ET
import re

# Identifier -------------------------------------------------------------
def create_identifier(output, record):
    '''Searches the 024 field'''
    identifierMRC = record.findall(".//datafield[@tag='024']")

    for item in identifierMRC:
        if item.find("subfield[@code='2']").text == "doi":
            identifier = ET.Element("identifier")
            identifier.attrib = {"identifierType":"DOI"}
            identifier.text = item.find("subfield[@code='a']").text

            output.append(identifier)
            
        elif item.find("subfield[@code='2']").text == "urn":
            altidentifiers = ET.Element("alternateIdentifiers")
            altidentifier = ET.SubElement(altidentifiers, "alternateIdentifier")
            altidentifier.attrib = {"alternateIdentifierType":item.find("subfield[@code='2']").text}
            altidentifier.text = item.find("subfield[@code='a']").text

            output.append(altidentifiers)

# Language -------------------------------------------------------------
def create_language(output, record):
    languageMRC = record.find(".//datafield[@tag='041']")

    language = ET.Element("language")
    language.text = languageMRC.find("subfield[@code='a']").text

    output.append(language)

# Creators -------------------------------------------------------------
def helper_create_creator(author, mainElement):
    creator = ET.SubElement(mainElement, "creator")

    creatorName = ET.SubElement(creator, "creatorName")
    creatorName.attrib = {"nameType":"Personal"}
    creatorName.text = author.find("subfield[@code='a']").text

    givenName = ET.SubElement(creator, "givenName")
    givenName.text = author.find("subfield[@code='a']").text.split(",")[1]

    familyName = ET.SubElement(creator, "familyName")
    familyName.text = author.find("subfield[@code='a']").text.split(",")[0]


def create_creator(output, record):
    main_authorMRC = record.find(".//datafield[@tag='100']")
    creators = ET.Element("creators")

    # create main Author
    helper_create_creator(main_authorMRC, creators)
    
    # create side-authors
    if record.findall(".//datafield[@tag='700']") != None:
        side_authorMRC = record.findall(".//datafield[@tag='700']")
        for author in side_authorMRC:
            helper_create_creator(author, creators)

    output.append(creators)

# Titles -------------------------------------------------------------
def create_title(output, record):
    titleMRC = record.find(".//datafield[@tag='245']")
    titles = ET.Element("titles")
    # ------------------------------ Main Title
    title = ET.SubElement(titles, "title")
    title.text = titleMRC.find("subfield[@code='a']").text
    # ------------------------------ Subtitle
    if titleMRC.find("subfield[@code='b']") != None:
        subtitle = ET.SubElement(titles, "title")
        subtitle.attrib = {
            "titleType":"Subtitle"
            }
        subtitle.text = titleMRC.find("subfield[@code='b']").text

    output.append(titles)

# publisher/publicationYear -------------------------------------------------------------
def create_publisher(output, record):
    # -------------publisher
    publisherMRC = record.find(".//datafield[@tag='264']")
    publisher = ET.Element("publisher")
    publisher.text = publisherMRC.find("subfield[@code='b']").text
    
    output.append(publisher)
    # -------------publication Year 
    publicationYear = ET.Element("publicationYear")
    pubDate = re.search("\d{4}", publisherMRC.find("subfield[@code='c']").text).group() # search for 4 digits in the "c" Subfield
    publicationYear.text = pubDate
    
    output.append(publicationYear)

# Size -------------------------------------------------------------
def create_size(output, record):
    sizeMRC = record.find(".//datafield[@tag='300']")
    sizes = ET.Element("sizes")
    size = ET.SubElement(sizes, "size")
    if re.search("(?<=\()\d+", sizeMRC.find("subfield[@code='a']").text) is None:
        size.text = record.find(".//datafield[@tag='300']").find("subfield[@code='a']").text
    else:
        pageNr = re.search("(?<=\()\d+", sizeMRC.find("subfield[@code='a']").text).group() # match 1-n digits after ()
        size.text = str(pageNr + " pages")

    output.append(sizes)

# Descriptions -------------------------------------------------------------
def create_descriptions(output, record):
    descriptions = ET.Element("descriptions")
    # ------------- Abstract
    abstractMRC = record.findall(".//datafield[@tag='520']")
    for item in abstractMRC:
        description = ET.SubElement(descriptions, "description")
        description.attrib = {"descriptionType":"Abstract"}
        # cut "eng: " or "ger: " from abstract text
        oldText = item.find("subfield[@code='a']").text
        toCut = re.search("^eng: |^ger: ", oldText).group()
        abstractText = oldText.replace(toCut, "")
        description.text = abstractText

    # ------------- Series Information
    description = ET.SubElement(descriptions, "description")
    description.attrib = {"descriptionType":"SeriesInformation"}
    # field 490 is not present - .find() returns None
    check_for_490 = record.find(".//datafield[@tag='490']")
    if check_for_490 is None:
        seriesInformationMRC = record.find(".//datafield[@tag='773']")
        description.text = str(
            seriesInformationMRC.find("subfield[@code='t']").text 
            + ", "
            + seriesInformationMRC.find("subfield[@code='g']").text
            )
    else:
        seriesInformationMRC = record.find(".//datafield[@tag='490']")
        description.text = str(
            seriesInformationMRC.find("subfield[@code='a']").text 
            + ", "
            + seriesInformationMRC.find("subfield[@code='v']").text
            )

    output.append(descriptions)

# fundingReferences -------------------------------------------------------------
def create_fundingReference(output, record):
    fundingMRC = record.findall(".//datafield[@tag='536']")
    fundingReferences = ET.Element("fundingReferences")

    for item in fundingMRC:
        fundingReference = ET.SubElement(fundingReferences, "fundingReference")
        funderName = ET.SubElement(fundingReference, "funderName")
        funderIdentifier = ET.SubElement(fundingReference, "funderIdentifier")
        funderIdentifier.attrib = {"funderIdentifierType":"Crossref Funder ID"}
        awardNumber = ET.SubElement(fundingReference, "awardNumber")
        awardNumber.text = item.find(("subfield[@code='f']")).text
        
        if item.find(("subfield[@code='a']")).text == "Fonds zur Förderung der Wissenschaftlichen Forschung":
            funderName.text = "Austrian Science Fund"
            funderIdentifier.text = "https://doi.org/10.13039/501100002428"
        elif item.find(("subfield[@code='a']")).text == "Österreichische Forschungsförderungsgesellschaft":
            funderName.text = "Österreichische Forschungsförderungsgesellschaft"
            funderIdentifier.text = "https://doi.org/10.13039/501100004955"
        elif  item.find(("subfield[@code='a']")).text == "Europäische Kommission":
            funderName.text = "European Commission"
            funderIdentifier.text = "https://doi.org/10.13039/501100000780"

    output.append(fundingReferences)

# ------------------------------- Fields with fixed Value ------------------------------
# RecourceType -------------------------------
def create_resourceType(output):
    resourceType = ET.Element("resourceType")
    resourceType.attrib = {"resourceTypeGeneral":"Text"}
    # resourceType.text = " "

    output.append(resourceType)

# Formats -------------------------------
def create_formats(output):
    formats = ET.Element("formats")
    formatDC = ET.SubElement(formats, "format")
    formatDC.text = "PDF"

    output.append(formats)
    
# Rights -------------------------------
def create_rights(output):
    rightsList = ET.Element("rightsList")
    rights = ET.SubElement(rightsList, "rights")
    rights.attrib = {
        "rightsIdentifier":"CC BY 4.0",
        "rightsURI":"https://creativecommons.org/licenses/by/4.0/legalcode"
        }
    # rights.text = " "

    output.append(rightsList)