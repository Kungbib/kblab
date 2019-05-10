<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
           xmlns:mets="http://www.loc.gov/METS/"
           xmlns:xlink="http://www.w3.org/1999/xlink"
           xmlns:mods="http://www.loc.gov/mods/v3"
           xmlns:premis="info:lc/xmlns/premis-v2"
           xmlns:mix="http://www.loc.gov/mix/v20"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:alto="http://www.loc.gov/standards/alto/ns-v2#"
           exclude-result-prefixes="xs"
           version="1.0">
    <xsl:output method="text"/>
    <xsl:strip-space elements="*"/>
    <xsl:param name="rwidth"><xsl:value-of select="/alto:alto/alto:Layout/alto:Page/@WIDTH"/></xsl:param>
    <xsl:param name="rheight"><xsl:value-of select="/alto:alto/alto:Layout/alto:Page/@HEIGHT"/></xsl:param>


    <xsl:template match="/alto:alto/alto:Layout/alto:Page">
        <xsl:variable name="width"><xsl:value-of select="@WIDTH"/></xsl:variable>
        <xsl:variable name="height"><xsl:value-of select="@HEIGHT"/></xsl:variable>
        {
            "width":"<xsl:value-of select="$rwidth"/>",
            "height":"<xsl:value-of select="$rheight"/>",
            
            "composedblocks": [
        <xsl:for-each select="alto:PrintSpace/alto:ComposedBlock">
                {
                    "i": "<xsl:value-of select="@ID"/>",
                    "c": [ "<xsl:value-of select="format-number(@HPOS div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@VPOS div $height,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@WIDTH div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@HEIGHT div $height,'######,######,##0.00000')"/>" ],
                    "textblocks" : [
            <xsl:for-each select="alto:TextBlock">
                        {
                            "i": "<xsl:value-of select="@ID"/>",
                            "c": [ "<xsl:value-of select="format-number(@HPOS div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@VPOS div $height,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@WIDTH div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@HEIGHT div $height,'######,######,##0.00000')"/>" ],
                            "words" : [
                <xsl:for-each select="alto:TextLine//alto:String">
                                { 
                                    "w":"<xsl:choose><xsl:when test="@SUBS_TYPE = 'HypPart1'"><xsl:value-of select="normalize-space(translate(@SUBS_CONTENT, '&quot;&#10;&#13;\', ''))"/></xsl:when><xsl:when test="@SUBS_TYPE = 'HypPart2'"></xsl:when><xsl:otherwise><xsl:value-of select="normalize-space(translate(@CONTENT, '&quot;&#10;&#13;\', ''))"/></xsl:otherwise></xsl:choose>",
                                    "c": [ "<xsl:value-of select="format-number(@HPOS div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@VPOS div $height,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@WIDTH div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@HEIGHT div $height,'######,######,##0.00000')"/>" ],
                                    "wc": "<xsl:value-of select="@WC"/>",
                                    "s": "<xsl:value-of select="/alto:alto/alto:Styles/alto:TextStyle[@ID = current()/@STYLEREFS]/@FONTSIZE"/>"
                                }<xsl:if test="position() != last()">,</xsl:if>
                </xsl:for-each>]
                        }<xsl:if test="position() != last()">,</xsl:if>
            </xsl:for-each>
                    ]<xsl:if test="alto:Illustration">,
                    "images" : [
            <xsl:for-each select="alto:Illustration">
                        {
                            "c": [ "<xsl:value-of select="format-number(@HPOS div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@VPOS div $height,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@WIDTH div $width,'######,######,##0.00000')"/>", "<xsl:value-of select="format-number(@HEIGHT div $height,'######,######,##0.00000')"/>" ],
                            "i": "<xsl:value-of select="@ID"/>"
                            }<xsl:if test="position() != last()">,</xsl:if>
            </xsl:for-each>
                    ]</xsl:if>
                }<xsl:if test="position() != last()">,</xsl:if>
        </xsl:for-each>
            ]
        }
    </xsl:template>
    
    <xsl:template match="text()"/>
</xsl:stylesheet>
