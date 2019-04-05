<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet  version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:alto="http://www.loc.gov/standards/alto/ns-v2#">
    <xsl:output method="xml" indent="yes" encoding="utf-8"/>
    <xsl:strip-space elements="*"/>

    
    <!-- ändra <Alto> till <alto> eller kopiera befitnlig, korrekt alto -->
    <xsl:template match="/Alto | /alto:alto">
        <xsl:element name="alto" namespace="http://www.loc.gov/standards/alto/ns-v2#">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!-- ändra <SourceImageInformation> till <sourceImageInformation> -->
    <xsl:template match="/Alto/Description/SourceImageInformation">
        <xsl:element name="sourceImageInformation" namespace="http://www.loc.gov/standards/alto/ns-v2#">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!-- fixa <TextStyle> -->
    <xsl:template match="/Alto/Styles/TextStyle">
        <xsl:element name="TextStyle" namespace="http://www.loc.gov/standards/alto/ns-v2#">
            <xsl:copy-of select="@*"/>

            <!-- fixa @FONTSTYLE -->
            <xsl:if test="@FONTSTYLE != ''">
            <xsl:attribute name="FONTSTYLE">
                <xsl:choose>
                    <xsl:when test="@FONTSTYLE = 'Bold'">bold</xsl:when>
                    <xsl:when test="@FONTSTYLE = 'Italic'">italics</xsl:when>
                    <xsl:when test="@FONTSTYLE = 'Underlined'">underline</xsl:when>
                    <xsl:when test="@FONTSTYLE = 'Bold,Italic'">bold italics</xsl:when>
                    <!-- ... -->
                    <!-- antingen fortsätta rada upp alla felaktiga @FONTSTYLE och samtliga kombinationer, eller göra något smartare --> 
                    <xsl:otherwise><xsl:value-of select="@FONTSTYLE"/></xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
        </xsl:if>

            <!-- lägg till @FONTTYPE -->
            <xsl:choose>
                <xsl:when test="@FONTFAMILY = 'Arial'"><xsl:attribute name="FONTTYPE">sans-serif</xsl:attribute></xsl:when>
                <xsl:when test="@FONTFAMILY = 'Times New Roman'"><xsl:attribute name="FONTTYPE">serif</xsl:attribute></xsl:when>
                <xsl:otherwise><xsl:value-of select="@FONTFAMILY"/></xsl:otherwise>
            </xsl:choose>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!-- lägg till @HPOS,@VPOS,@WIDTH,@HEIGHT -->
    <xsl:template match="/Alto/Layout/Page/PrintSpace/ComposedBlock">
        <xsl:element name="ComposedBlock" namespace="http://www.loc.gov/standards/alto/ns-v2#">
            <!--xsl:attribute name="HPOS"><xsl:value-of select="fn:min(*/@HPOS)"/></xsl:attribute-->
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
        
    <!-- lägg till rätt namespace på alla noder som har tom motsvarande. OBS! lägger även alto-namespace -->
    <!-- på noder som explicit har tomt sådant genom xmls="". Fix behövs typ "alla noder med tom ns utan -->
    <!-- attributet xmlns="" i föräldranoder" -->
    <xsl:template match="*[namespace-uri()='']">
        <xsl:element name="{name()}" namespace="http://www.loc.gov/standards/alto/ns-v2#">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
