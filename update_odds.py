la, lb = stima_lambda_da_quote(q1, qx, q2, qo25, qu25)

        qgg = round(float(np.mean(qgg_list)), 2) if qgg_list else round(qo25 * 0.96, 2)
        qob = round(qo25 * 1.18, 2)
        p1x = (1 / q1) + (1 / qx)
        q1x = round(max(1.15, (1 / p1x) * 1.25), 2)

        palinsesto_pulito.append({
            "ora": dt_it.strftime("%H:%M"),
            "lega": lega,
            "m": f"{home} - {away}",
            "la": la,
            "lb": lb,
            "qo25": qo25,
            "qgg": qgg,
            "qob": qob,
            "qu25": qu25,
            "q1x": q1x
        })

    palinsesto_pulito.sort(key=lambda x: x["ora"])

    os.makedirs("data", exist_ok=True)
    output = {
        "aggiornato_il": datetime.now(ROME_TZ).strftime("%d/%m/%Y alle %H:%M"),
        "totale_match": len(palinsesto_pulito),
        "partite": palinsesto_pulito
    }

    with open("data/palinsesto.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"Salvati {len(palinsesto_pulito)} match per oggi.")

if __name__ == "__main__":
    fetch_palinsesto()
