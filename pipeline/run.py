"""Orchestrateur · bronze → silver → gold"""
from pipeline.bronze import ingest
from pipeline.silver import transform
from pipeline.gold import indicators


def main():
    print("== BRONZE ==")
    ingest.run()
    print("== SILVER ==")
    transform.run()
    print("== GOLD ==")
    indicators.build()
    print("done.")


if __name__ == "__main__":
    main()
