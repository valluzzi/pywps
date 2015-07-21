from pywps import configuration, E, OWS, WPS, OGCTYPE, NAMESPACES
from pywps.inout import basic


class ComplexInput(basic.ComplexInput):
    """
    :param identifier: The name of this input.
    :param allowed_formats: Allowed formats for this input. Should be a list of
                    one or more :class:`~Format` objects.
    :param data_format: Format of the passed input. Should be :class:`~Format` object
    """

    def __init__(self, identifier, title, allowed_formats=None, data_format=None, abstract='', metadata=[], min_occurs='1',
                 max_occurs='1', as_reference=False):
        basic.ComplexInput.__init__(self, identifier=identifier, title=title, abstract=abstract, data_format=data_format)
        self.allowed_formats = allowed_formats
        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference
        self.url = ''
        self.method = ''
        self.max_size = int(0)

    def calculate_max_input_size(self):
        """Calculates maximal size for input file based on configuration
        and units

        :return: maximum file size bytes
        """
        maxSize = configuration.get_config_value('server', 'maxsingleinputsize')
        self.max_size = configuration.get_size_mb(maxSize)

    def describe_xml(self):
        default_format_el = self.allowed_formats[0].describe_xml()
        supported_format_elements = [f.describe_xml() for f in self.allowed_formats]
        
        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = self.min_occurs
        doc.attrib['maxOccurs'] = self.max_occurs

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        if self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        doc.append(
            E.ComplexData(
                E.Default(default_format_el),
                E.Supported(*supported_format_elements)
            )
        )

        return doc
    
    def execute_xml(self):
        """Render Execute response XML node


        :return: node
        :rtype: ElementMaker
        """
        node = None
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.url
        if self.data_format:
            if self.data_format.mime_type:
                doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                doc.attrib['schema'] = self.data_format.schema
        if self.method.upper() == 'POST' or self.method.upper() == 'GET':
            doc.attrib['method'] = self.method.upper()
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()
        complex_doc = WPS.ComplexData(self.data)

        if self.data_format:
            if self.data_format.mime_type:
                complex_doc.attrib['mimeType'] = self.data_format.mime_type
            if self.data_format.encoding:
                complex_doc.attrib['encoding'] = self.data_format.encoding
            if self.data_format.schema:
                complex_doc.attrib['schema'] = self.data_format.schema
        doc.append(complex_doc)
        return doc


class LiteralInput(basic.LiteralInput):
    """
    :param identifier: The name of this input.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    """

    def __init__(self, identifier, title, data_type='string', abstract='',
                 metadata=[], uoms=[], default='',
                 min_occurs='1', max_occurs='1', as_reference=False):
        basic.LiteralInput.__init__(self, identifier=identifier, title=title,
                                    abstract=abstract, data_type=data_type, uoms=uoms)
        self.metadata = metadata
        self.default = default
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference

    def describe_xml(self):
        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = self.min_occurs
        doc.attrib['maxOccurs'] = self.max_occurs

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        if self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        literal_data_doc = E.LiteralData()

        if self.data_type:
            data_type = OWS.DataType(self.data_type)
            data_type.attrib['{%s}reference' % NAMESPACES['ows']] = OGCTYPE[self.data_type]
            literal_data_doc.append(data_type)

        if self.uoms:
            default_uom_element = self.uoms[0].describe_xml()
            supported_uom_elements = [u.describe_xml() for u in self.uoms]

            literal_data_doc.append(
                E.UOMs(
                    E.Default(default_uom_element),
                    E.Supported(*supported_uom_elements)
                )
            )

        doc.append(literal_data_doc)

        # TODO: refer to table 29 and 30
        literal_data_doc.append(OWS.AnyValue())

        if self.default:
            doc.append(E.DefaultValue(self.default))

        return doc

    def execute_xml(self):
        """Render Execute response XML node

        :return: node
        :rtype: ElementMaker
        """
        node = None
        if self.as_reference:
            node = self._execute_xml_reference()
        else:
            node = self._execute_xml_data()

        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )
        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))
        doc.append(node)

        return doc

    def _execute_xml_reference(self):
        """Return Reference node
        """
        doc = WPS.Reference()
        doc.attrib['{http://www.w3.org/1999/xlink}href'] = self.stream
        if self.method.upper() == 'POST' or self.method.upper() == 'GET':
            doc.attrib['method'] = self.method.upper()
        return doc

    def _execute_xml_data(self):
        """Return Data node
        """
        doc = WPS.Data()
        literal_doc = WPS.LiteralData(self.data)

        if self.data_type:
            literal_doc.attrib['dataType'] = self.data_type
        if self.uom:
            literal_doc.attrib['uom'] = self.uom
        doc.append(literal_doc)
        return doc


class BoundingBoxInput(basic.BBoxInput):
    """
    :param identifier: The name of this input.
    :param data_type: Type of literal input (e.g. `string`, `float`...).
    """

    def __init__(self, identifier, title, crss, abstract='',
                 dimensions=2, metadata=[], min_occurs='1',
                 max_occurs='1', as_reference=False):
        basic.BBoxInput.__init__(self, identifier, title=title,
                                 abstract=abstract, crss=crss,
                                 dimensions=dimensions)

        self.metadata = metadata
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.as_reference = as_reference

    def describe_xml(self):
        doc = E.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        doc.attrib['minOccurs'] = self.min_occurs
        doc.attrib['maxOccurs'] = self.max_occurs

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        if self.metadata:
            doc.append(OWS.Metadata(*self.metadata))

        bbox_data_doc = E.BoundingBoxData()
        doc.append(bbox_data_doc)

        default_doc = E.Default()
        default_doc.append(E.CRS(self.crss[0]))

        supported_doc = E.Supported()
        for c in self.crss:
            supported_doc.append(E.CRS(c))

        bbox_data_doc.append(default_doc)
        bbox_data_doc.append(supported_doc)

        return doc

    def execute_xml(self):
        doc = WPS.Input(
            OWS.Identifier(self.identifier),
            OWS.Title(self.title)
        )

        if self.abstract:
            doc.append(OWS.Abstract(self.abstract))

        bbox_data_doc = OWS.BoundingBox()

        bbox_data_doc.attrib['crs'] = self.crs
        bbox_data_doc.attrib['dimensions'] = str(self.dimensions)

        bbox_data_doc.append(OWS.LowerCorner('{0[0]} {0[1]}'.format(self.data)))
        bbox_data_doc.append(OWS.UpperCorner('{0[2]} {0[3]}'.format(self.data)))

        doc.append(bbox_data_doc)

        return doc
