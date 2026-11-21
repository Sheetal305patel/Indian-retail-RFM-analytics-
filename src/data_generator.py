"""
Indian Consumer Market Enterprise Data Generator
Simulates omnichannel retail transactions modeled after major Indian consumer giants
(Tata Consumer / Tata Neu, Reliance Retail / Ajio, Nykaa, HUL, ITC).
- 100% Indian consumer demographics across Metro, Tier 2, and Tier 3 cities.
- Native pricing in Indian Rupees (INR - ₹).
- Real-world Indian payments: UPI (58%), Cash on Delivery with RTO bounce (28%), Cards (10%), NetBanking (4%).
- WhatsApp-first CRM architecture under India's DPDP Act 2023 & TRAI DND regulations.
"""
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    RAW_DATA_DIR,
    INDIAN_CITY_TIERS,
    PAYMENT_METHODS
)

def generate_enterprise_dataset(
    num_customers: int = 4000,
    num_orders: int = 20000,
    seed: int = 42,
    as_of_date: str = "2026-11-20"
):
    """
    Generates realistic Indian omnichannel consumer retail data in INR (₹).
    """
    random.seed(seed)
    np.random.seed(seed)
    as_of_dt = datetime.strptime(as_of_date, "%Y-%m-%d")
    start_date = as_of_dt - timedelta(days=540) # 18-month historical observation window

    print(f"Generating realistic Indian consumer enterprise dataset: {num_customers} consumers, ~{num_orders} orders in INR (₹)...")

    # 1. Product Catalog Modeled on Indian Consumer Giants
    # (Tata Consumer, Reliance Ajio, Nykaa Beauty, HUL Skincare, BoAt Electronics)
    catalog = [
        {"product_id": "SKU-BEA-01", "name": "Niacinamide 10% Clarifying Face Serum 30ml", "category": "Beauty & Skincare", "base_price_inr": 649.0, "cost_ratio": 0.22, "return_prob": 0.02},
        {"product_id": "SKU-BEA-02", "name": "Ultra-Matte Sunscreen Gel SPF 50 PA++++", "category": "Beauty & Skincare", "base_price_inr": 549.0, "cost_ratio": 0.24, "return_prob": 0.02},
        {"product_id": "SKU-BEA-03", "name": "Organic Red Onion Hair Fall Control Oil 200ml", "category": "Haircare & Wellness", "base_price_inr": 499.0, "cost_ratio": 0.20, "return_prob": 0.01},
        {"product_id": "SKU-BEA-04", "name": "Matte Liquid Lipstick Longwear Festive Edition", "category": "Beauty & Cosmetics", "base_price_inr": 799.0, "cost_ratio": 0.25, "return_prob": 0.03},
        {"product_id": "SKU-APP-01", "name": "Pure Breathable Cotton Daily Kurta / Shirt", "category": "Apparel & Ethnic", "base_price_inr": 1299.0, "cost_ratio": 0.32, "return_prob": 0.08},
        {"product_id": "SKU-APP-02", "name": "Comfort Stretch Slim-Fit Denim Jeans", "category": "Apparel & Western", "base_price_inr": 2199.0, "cost_ratio": 0.36, "return_prob": 0.10},
        {"product_id": "SKU-APP-03", "name": "Handcrafted Festive Embroidered Anarkali Set", "category": "Apparel & Festive", "base_price_inr": 4499.0, "cost_ratio": 0.38, "return_prob": 0.12},
        {"product_id": "SKU-FTW-01", "name": "Cushioned Street Pro Running Sneakers", "category": "Footwear & Athleisure", "base_price_inr": 2799.0, "cost_ratio": 0.40, "return_prob": 0.11},
        {"product_id": "SKU-FTW-02", "name": "Handcrafted Vegan Leather Formal Slip-ons", "category": "Footwear & Formal", "base_price_inr": 3299.0, "cost_ratio": 0.42, "return_prob": 0.09},
        {"product_id": "SKU-ELE-01", "name": "Spatial Audio ANC True Wireless Earbuds", "category": "Smart Electronics", "base_price_inr": 1999.0, "cost_ratio": 0.34, "return_prob": 0.05},
        {"product_id": "SKU-ELE-02", "name": "AMOLED Display Bluetooth Calling Smartwatch", "category": "Smart Electronics", "base_price_inr": 2999.0, "cost_ratio": 0.35, "return_prob": 0.06},
        {"product_id": "SKU-FMC-01", "name": "Artisanal Single-Origin Darjeeling Tea 250g", "category": "Gourmet Foods & Beverages", "base_price_inr": 450.0, "cost_ratio": 0.28, "return_prob": 0.01},
        {"product_id": "SKU-FMC-02", "name": "Cold-Pressed Organic Virgin Coconut Oil 500ml", "category": "Gourmet Foods & Beverages", "base_price_inr": 380.0, "cost_ratio": 0.30, "return_prob": 0.01}
    ]
    df_products = pd.DataFrame(catalog)

    # 2. Indian Consumers Generation Across City Tiers
    # 45% Metro, 35% Tier 2, 20% Tier 3
    tier_choices = ["Tier 1 - Metro", "Tier 2 - Emerging Hubs", "Tier 3 - Bharat Growth Belt"]
    tier_weights = [0.45, 0.35, 0.20]

    first_names = [
        "Aarav", "Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Aditya", "Pooja", "Vikram", "Neha",
        "Siddharth", "Kavita", "Karan", "Divya", "Arjun", "Deepika", "Manish", "Shreya", "Amit", "Tanvi",
        "Nikhil", "Meera", "Varun", "Rhea", "Gaurav", "Anjali", "Harsh", "Simran", "Pranav", "Ishita",
        "Suresh", "Lakshmi", "Venkatesh", "Swati", "Rajesh", "Sunita", "Manoj", "Bhavna", "Kunal", "Preeti"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Mehta", "Singh", "Chopra",
        "Mukherjee", "Deshmukh", "Bose", "Kulkarni", "Aggarwal", "Kapoor", "Bhatia", "Joshi", "Das",
        "Rao", "Pillai", "Menon", "Chauhan", "Bhattacharya", "Banerjee", "Pandey", "Trivedi", "Saxena"
    ]
    domains = ["gmail.com", "yahoo.co.in", "outlook.com", "rediffmail.com", "icloud.com"]

    customer_records = []
    contact_records = []
    identity_links = []

    for i in range(1, num_customers + 1):
        cust_id = f"IND-CUST-{i:05d}"
        tier = random.choices(tier_choices, weights=tier_weights)[0]
        city = random.choice(INDIAN_CITY_TIERS[tier])
        first_seen = start_date + timedelta(days=random.randint(0, 480))

        # Identity resolution types (Loyalty cards like Tata NeuCoins / Reliance One / Nykaa Prive)
        id_type = random.choices(["verified_account", "loyalty_member", "guest_resolved"], weights=[0.58, 0.30, 0.12])[0]

        # Indian Marketing Permissions (WhatsApp-First CRM under DPDP Act 2023 & TRAI DND)
        whatsapp_opt_in = random.choices([True, False], weights=[0.84, 0.16])[0] # 84% WhatsApp consent
        sms_opt_in = random.choices([True, False], weights=[0.68, 0.32])[0]      # 68% SMS consent
        push_opt_in = random.choices([True, False], weights=[0.55, 0.45])[0]     # 55% App Push consent
        email_opt_in = random.choices([True, False], weights=[0.42, 0.58])[0]    # 42% Email consent

        # TRAI DND / Legal suppression rate in India (2.5%)
        suppression_flag = random.choices([False, True], weights=[0.975, 0.025])[0]

        customer_records.append({
            "customer_id": cust_id,
            "country": "India",
            "city_tier": tier,
            "city_location": city,
            "currency": "INR",
            "identity_status": id_type,
            "first_seen_at": first_seen.strftime("%Y-%m-%d %H:%M:%S"),
            "whatsapp_opt_in": whatsapp_opt_in,
            "sms_opt_in": sms_opt_in,
            "push_opt_in": push_opt_in,
            "email_opt_in": email_opt_in,
            "suppression_flag": suppression_flag
        })

        # Protected contact PII (Physical separation under DPDP Act 2023)
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@{random.choice(domains)}"
        phone = f"+91{random.choice(['98', '97', '99', '88', '70', '81'])}{random.randint(10000000, 99999999)}"

        contact_records.append({
            "customer_id": cust_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "phone": phone,
            "city": city.split(" (")[0]
        })

        # Identity Graph Tokens
        identity_links.append({
            "customer_id": cust_id,
            "identifier_type": "PHONE_NUMBER",
            "identifier_val": phone
        })
        if id_type == "loyalty_member":
            identity_links.append({
                "customer_id": cust_id,
                "identifier_type": "LOYALTY_CARD",
                "identifier_val": f"NEU-PRIVILEGE-{100000 + i}"
            })
        if random.random() < 0.28:
            identity_links.append({
                "customer_id": cust_id,
                "identifier_type": "DEVICE_ADID",
                "identifier_val": f"GAID-{uuid.uuid4().hex[:12].upper()}"
            })

    df_customers = pd.DataFrame(customer_records)
    df_contacts = pd.DataFrame(contact_records)
    df_identity = pd.DataFrame(identity_links)

    # 3. Omnichannel Order Generation (INR - ₹)
    cust_ids = df_customers["customer_id"].tolist()
    # Pareto Power-Law: 15% VIP brand loyalists, 25% repeat shoppers, 60% infrequent
    cust_weights = np.random.pareto(a=1.45, size=len(cust_ids))
    cust_weights /= cust_weights.sum()

    channels = ["d2c_app", "d2c_web", "pos_store_identified", "pos_store_anonymous", "quick_commerce"]
    channel_weights = [0.48, 0.28, 0.14, 0.06, 0.04] # 6% anonymous offline store checkouts

    pm_list = ["UPI", "COD", "Cards", "NetBanking_Wallets"]
    pm_weights = [PAYMENT_METHODS[pm]["share"] for pm in pm_list]

    orders = []
    order_items = []
    order_id_counter = 500001

    for _ in range(num_orders):
        order_id = f"IND-ORD-{order_id_counter}"
        order_id_counter += 1

        chosen_channel = random.choices(channels, weights=channel_weights)[0]

        if chosen_channel == "pos_store_anonymous":
            chosen_cust = None
            first_seen_ref = start_date
            tier = random.choices(tier_choices, weights=tier_weights)[0]
            city = random.choice(INDIAN_CITY_TIERS[tier])
        else:
            chosen_cust = np.random.choice(cust_ids, p=cust_weights)
            cust_row = df_customers[df_customers["customer_id"] == chosen_cust].iloc[0]
            first_seen_ref = datetime.strptime(cust_row["first_seen_at"], "%Y-%m-%d %H:%M:%S")
            tier = cust_row["city_tier"]
            city = cust_row["city_location"]

        # Order Timestamp
        days_after_first = max(1, (as_of_dt - first_seen_ref).days)
        order_time = first_seen_ref + timedelta(
            days=random.randint(0, days_after_first),
            hours=random.randint(8, 23),
            minutes=random.randint(0, 59)
        )
        if order_time > as_of_dt:
            order_time = as_of_dt - timedelta(hours=random.randint(1, 48))

        # Payment Method Selection
        payment_method = random.choices(pm_list, weights=pm_weights)[0]

        # Indian Retail Core Dynamic: Cash on Delivery (COD) Return-To-Origin (RTO)
        # COD has ~25% RTO failure rate (doorstep refusal). Prepaid UPI / Cards have <2.5% return rate!
        order_status = "COMPLETED"
        if payment_method == "COD":
            if random.random() < PAYMENT_METHODS["COD"]["rto_failure_rate"]:
                order_status = "RTO" # Return-To-Origin: Courier bounced, zero revenue collected
        elif random.random() < 0.025:
            order_status = "CANCELLED" # Pre-dispatch cancellation
        elif random.random() < 0.010:
            order_status = "FRAUD"
        elif random.random() < 0.005:
            order_status = "TEST"
        elif random.random() < 0.035:
            order_status = "REFUNDED" # Delivered, but returned by customer within 7-day window

        # Basket items (1 to 4 products)
        num_items = random.choices([1, 2, 3, 4], weights=[0.58, 0.26, 0.12, 0.04])[0]
        selected_prods = df_products.sample(n=num_items, replace=True)

        gross_inr = 0.0
        discount_inr = 0.0
        refund_inr = 0.0
        cost_inr = 0.0

        for _, prod in selected_prods.iterrows():
            qty = random.choices([1, 2], weights=[0.92, 0.08])[0]
            unit_price = prod["base_price_inr"]
            line_gross = round(unit_price * qty, 2)

            # Promotional discount (Diwali / End of Season / Welcome coupon)
            disc_pct = random.choices([0.0, 0.10, 0.15, 0.20], weights=[0.60, 0.22, 0.12, 0.06])[0]
            line_discount = round(line_gross * disc_pct, 2)
            line_net = line_gross - line_discount
            line_cost = round(unit_price * prod["cost_ratio"] * qty, 2)

            return_qty = 0
            if order_status in ["REFUNDED", "RTO"]:
                return_qty = qty
            elif order_status == "COMPLETED" and random.random() < prod["return_prob"]:
                return_qty = 1 # partial customer return

            line_refund = round((line_net / qty) * return_qty, 2) if qty > 0 else 0.0

            gross_inr += line_gross
            discount_inr += line_discount
            refund_inr += line_refund
            cost_inr += line_cost

            order_items.append({
                "order_id": order_id,
                "product_id": prod["product_id"],
                "quantity": qty,
                "unit_price_inr": unit_price,
                "discount_inr": line_discount,
                "net_line_inr": line_net,
                "return_quantity": return_qty,
                "refund_inr": line_refund,
                "product_cost_inr": line_cost,
                "contribution_margin_inr": round(line_net - line_refund - (line_cost * (qty - return_qty) / max(1, qty)), 2)
            })

        # Net Sales Calculation in INR (₹)
        if order_status in ["CANCELLED", "FRAUD", "TEST", "RTO", "REFUNDED"]:
            net_sales_inr = 0.0
        else:
            net_sales_inr = round(gross_inr - discount_inr - refund_inr, 2)

        # Logistics & Gateway Cost Deduction for Real Indian Unit Economics:
        # Gateway fee (0% on UPI, 1.8% on Cards)
        gateway_fee = round(net_sales_inr * PAYMENT_METHODS[payment_method].get("gateway_fee_pct", 0.0), 2)
        # 3PL Courier Logistics penalty on RTO (Delhivery / BlueDart forward + reverse charge)
        rto_courier_loss = PAYMENT_METHODS["COD"]["reverse_logistics_loss_inr"] if order_status == "RTO" else 0.0
        
        # Contribution Margin = Net Merchandise Sales - Product Cost - Gateway Fee - RTO Courier Penalty
        if net_sales_inr > 0:
            contribution_margin = round(net_sales_inr - cost_inr - gateway_fee, 2)
        else:
            contribution_margin = round(-rto_courier_loss, 2) # true negative margin on RTO!

        orders.append({
            "order_id": order_id,
            "customer_id": chosen_cust,
            "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": order_status,
            "country": "India",
            "city_tier": tier,
            "city_location": city,
            "payment_method": payment_method,
            "channel": chosen_channel,
            "currency": "INR",
            "gross_amount": round(gross_inr, 2),
            "discount_amount": round(discount_inr, 2),
            "refund_amount": round(refund_inr, 2),
            "net_sales_amount": net_sales_inr,
            "net_sales_inr": net_sales_inr,
            "product_cost_inr": round(cost_inr, 2),
            "gateway_fee_inr": gateway_fee,
            "rto_courier_loss_inr": rto_courier_loss,
            "contribution_margin_inr": contribution_margin
        })

    df_orders = pd.DataFrame(orders)
    df_order_items = pd.DataFrame(order_items)

    # Save curated raw files
    df_customers.to_csv(RAW_DATA_DIR / "customers.csv", index=False)
    df_contacts.to_csv(RAW_DATA_DIR / "customer_contacts_pii.csv", index=False)
    df_identity.to_csv(RAW_DATA_DIR / "identity_links.csv", index=False)
    df_orders.to_csv(RAW_DATA_DIR / "orders.csv", index=False)
    df_order_items.to_csv(RAW_DATA_DIR / "order_items.csv", index=False)
    df_products.to_csv(RAW_DATA_DIR / "products.csv", index=False)

    total_gross = df_orders["gross_amount"].sum()
    total_net = df_orders["net_sales_inr"].sum()
    rto_orders = df_orders[df_orders["order_status"] == "RTO"]

    print("Indian Consumer Enterprise Dataset Generated Successfully:")
    print(f" - Consumers: {len(df_customers):,} across Metro ({tier_weights[0]*100:.0f}%), Tier 2 ({tier_weights[1]*100:.0f}%), Tier 3 ({tier_weights[2]*100:.0f}%)")
    print(f" - Orders: {len(df_orders):,} (Identified: {df_orders['customer_id'].notna().sum():,}, Anonymous Store Walk-ins: {df_orders['customer_id'].isna().sum():,})")
    print(f" - Gross GMV: ₹{total_gross:,.2f} | Net Sales (NMV): ₹{total_net:,.2f}")
    print(f" - Cash on Delivery (COD) RTO Deliveries Bounced: {len(rto_orders):,} ({len(rto_orders)/max(1, (df_orders['payment_method']=='COD').sum())*100:.1f}% of COD)")
    print(f" - Logistics Cost Burn on COD RTO: ₹{rto_orders['rto_courier_loss_inr'].sum():,.2f}")

    return {
        "customers": df_customers,
        "contacts": df_contacts,
        "orders": df_orders,
        "order_items": df_order_items
    }

if __name__ == "__main__":
    generate_enterprise_dataset()
