import json
from abc import ABC

from YBLEGACY import qsatype

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.upload_sync import UploadSync

from controllers.base.magento2.products.serializers.configurable_product_serializer import ConfigurableProductSerializer
from controllers.base.magento2.products.serializers.simple_product_serializer import SimpleProductSerializer
from controllers.base.magento2.products.serializers.product_link_serializer import ProductLinkSerializer

class ProductsUpload(UploadSync, ABC):

    product_url = "<host>/rest/V1/products"
    product_test_url = "<testhost>/rest/V1/products"

    link_url = "<host>/rest/all/V1/configurable-products/child"
    link_test_url = "<testhost>/rest/all/V1/configurable-products/child"

    idlinea = None
    idsincro = None
    referencia = None
    indice_tallas = None
    stock_disponible = None

    def __init__(self, process_name, params=None):
        super().__init__(process_name, Magento2Driver(), params)

        self.indice_tallas = []
        self.stock_disponible = False
        self.store_id = "all"

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        data[0]["indice_tallas"] = self.indice_tallas
        data[0]["stock_disponible"] = self.stock_disponible
        data[0]["store_id"] = "all"

        # configurable_product_default = self.get_configurable_product_serializer().serialize(data[0])
        # data[0]["store_id"] = "ES"
        # configurable_product_es = self.get_configurable_product_serializer().serialize(data[0])
        # data[0]["store_id"] = "EN"
        # configurable_product_en = self.get_configurable_product_serializer().serialize(data[0])
        simple_products_default = []
        # simple_products_es = []
        # simple_products_en = []
        # product_links = []

        for row in data:
            row["store_id"] = "all"
            simple_products_default.append(self.get_simple_product_serializer().serialize(row))
            # row["store_id"] = "ES"
            # simple_products_es.append(self.get_simple_product_serializer().serialize(row))
            # row["store_id"] = "EN"
            # simple_products_en.append(self.get_simple_product_serializer().serialize(row))
            # product_links.append(self.get_product_link_serializer().serialize(row))

        # if not configurable_product_default and not simple_products_default and not product_links:
        #     return False

        # if product_links[0] == False:
        #     product_links = False


        return {
            # "configurable_product_default": configurable_product_default,
            # "configurable_product_es": configurable_product_es,
            # "configurable_product_en": configurable_product_en,
            "simple_products_default": simple_products_default,
            # "simple_products_es": simple_products_es,
            # "simple_products_en": simple_products_en,
            # "product_links": [],
        }

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar productos' AND NOT sincronizado ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, s.disponible, a.mgdescripcion, a.mgdescripcioncorta")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a ON lsc.idobjeto = a.referencia LEFT JOIN stocks s ON a.referencia = s.referencia")
        q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, s.disponible, a.mgdescripcion, a.mgdescripcioncorta".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.referencia = body[0]["lsc.idobjeto"]

        for row in body:
            if "s.disponible" not in row or row["s.disponible"] is None:
                row["s.disponible"] = 0
            if row["s.disponible"] > 0:
                self.stock_disponible = True

        return body

    def get_configurable_product_serializer(self):
        return ConfigurableProductSerializer()

    def get_simple_product_serializer(self):
        return SimpleProductSerializer()

    def get_product_link_serializer(self):
        return ProductLinkSerializer()

    def send_data(self, data):
        product_url = self.product_url if self.driver.in_production else self.product_test_url
        link_url = self.link_url if self.driver.in_production else self.link_test_url

        # if data["configurable_product_default"]:
        #     self.send_request("post", url=product_url.format("all"), data=json.dumps(data["configurable_product_default"]))

        # if data["configurable_product_es"]:
        #     self.send_request("post", url=product_url.format("ES"), data=json.dumps(data["configurable_product_es"]))

        # if data["configurable_product_en"]:
        #     self.send_request("post", url=product_url.format("EN"), data=json.dumps(data["configurable_product_en"]))

        if data["simple_products_default"]:
            for simple_product in data["simple_products_default"]:
                # self.send_request("post", url=product_url.format("all"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url, data=json.dumps(simple_product))

        # if data["simple_products_es"]:
        #     for simple_product in data["simple_products_es"]:
        #         self.send_request("post", url=product_url.format("ES"), data=json.dumps(simple_product))

        # if data["simple_products_en"]:
        #     for simple_product in data["simple_products_en"]:
        #         self.send_request("post", url=product_url.format("EN"), data=json.dumps(simple_product))

        # if data["product_links"]:
        #     for product_link in data["product_links"]:
        #         self.send_request("post", url=link_url.format(data["configurable_product_default"]["product"]["sku"]), data=json.dumps(product_link))

        return data

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))

        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        if not lineas_no_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = FALSE WHERE idsincro = '{}'".format(self.idsincro))

        self.log("Éxito", "Productos sincronizados correctamente (referencia: {})".format(self.referencia))

        return self.small_sleep