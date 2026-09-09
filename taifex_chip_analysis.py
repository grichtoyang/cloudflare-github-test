from taifex_loader import load_taifex


class TAIFEXChipAnalysis:
    """TAIFEX 三大法人籌碼分析 V1.0"""

    def __init__(self, target_date=None):
        self.data = load_taifex(target_date)

    # ==========================================
    # 1. 台指期資料
    # ==========================================

    def get_futures_price(self):
        return self.data["futures_price"]

    def get_near_month(self):
        """
        取得近月台指期。

        目前資料來源已依 TAIFEX 回傳順序提供，
        第一筆視為近月。
        """

        futures = self.get_futures_price()

        if not futures:
            return None

        return futures[0]

    # ==========================================
    # 2. 三大法人期貨
    # ==========================================

    def get_institutional(self):
        return self.data["futures_institutional"]

    def get_institutional_oi(self):
        return self.data["futures_institutional_oi"]

    # ==========================================
    # 3. 法人分類
    # ==========================================

    def _institution_map(self, rows):
        result = {}

        for row in rows:
            institution = row.get("institution")

            if institution:
                result[institution] = row

        return result

    # ==========================================
    # 4. 取得法人淨交易量
    # ==========================================

    def get_net_volume(self):
        rows = self.get_institutional()

        result = {}

        for row in rows:
            institution = row.get("institution")

            if institution:
                result[institution] = row.get(
                    "net_volume"
                )

        return result

    # ==========================================
    # 5. 取得法人未平倉
    # ==========================================

    def get_net_oi(self):
        rows = self.get_institutional_oi()

        result = {}

        for row in rows:
            institution = row.get("institution")

            if institution:
                result[institution] = row.get(
                    "net_oi"
                )

        return result

    # ==========================================
    # 6. 法人合計
    # ==========================================

    def get_total_net_volume(self):
        values = self.get_net_volume().values()

        return sum(
            value for value in values
            if isinstance(value, (int, float))
        )

    def get_total_net_oi(self):
        values = self.get_net_oi().values()

        return sum(
            value for value in values
            if isinstance(value, (int, float))
        )

    # ==========================================
    # 7. 建立完整摘要
    # ==========================================

    def summary(self):
        near = self.get_near_month()

        return {
            "date": self.data["date"],
            "source": self.data["source"],
            "proxy": self.data["proxy"],

            "near_month": near,

            "institutional_net_volume":
                self.get_net_volume(),

            "institutional_net_oi":
                self.get_net_oi(),

            "total_net_volume":
                self.get_total_net_volume(),

            "total_net_oi":
                self.get_total_net_oi(),
        }


# ==========================================
# Command Line Test
# ==========================================

if __name__ == "__main__":

    analysis = TAIFEXChipAnalysis()

    result = analysis.summary()

    print("=" * 60)
    print("TAIFEX Chip Analysis V1.0")
    print("=" * 60)

    print(f"Date   : {result['date']}")
    print(f"Source : {result['source']}")
    print(f"Proxy  : {result['proxy']}")

    print()
    print("-" * 60)
    print("近月台指期")
    print("-" * 60)

    near = result["near_month"]

    if near:
        print(f"Contract : {near.get('contract_month')}")
        print(f"Open     : {near.get('open')}")
        print(f"High     : {near.get('high')}")
        print(f"Low      : {near.get('low')}")
        print(f"Close    : {near.get('close')}")
        print(f"Change   : {near.get('change')}")
        print(f"Volume   : {near.get('total_volume')}")
        print(f"OI       : {near.get('open_interest')}")

    print()
    print("-" * 60)
    print("三大法人期貨淨交易量")
    print("-" * 60)

    for institution, value in result[
        "institutional_net_volume"
    ].items():
        print(f"{institution:20} {value}")

    print(
        f"\n法人合計淨交易量: "
        f"{result['total_net_volume']}"
    )

    print()
    print("-" * 60)
    print("三大法人未平倉")
    print("-" * 60)

    for institution, value in result[
        "institutional_net_oi"
    ].items():
        print(f"{institution:20} {value}")

    print(
        f"\n法人合計未平倉: "
        f"{result['total_net_oi']}"
    )

    print()
    print("=" * 60)
    print("TAIFEX Chip Analysis 成功")
    print("=" * 60)
