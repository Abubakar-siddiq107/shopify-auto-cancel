const axios = require('axios');
const dayjs = require('dayjs');

const SHOP = process.env.SHOPIFY_STORE;
const TOKEN = process.env.SHOPIFY_TOKEN;

(async () => {
  try {
    const cutoffDate = dayjs().subtract(4, 'day').toISOString();
    console.log(`🔍 Looking for orders before: ${cutoffDate}`);

    const response = await axios.get(`https://${SHOP}/admin/api/2023-10/orders.json`, {
      headers: {
        'X-Shopify-Access-Token': TOKEN,
        'Content-Type': 'application/json',
      },
      params: {
        status: 'open',
        fulfillment_status: 'unfulfilled',
        created_at_max: cutoffDate,
        limit: 250
      }
    });

    const orders = response.data.orders;
    if (!orders.length) {
      console.log('✅ No unfulfilled orders older than 4 days found.');
      return;
    }

    for (const order of orders) {
      try {
        await axios.post(
          `https://${SHOP}/admin/api/2023-10/orders/${order.id}/cancel.json`,
          {},
          {
            headers: {
              'X-Shopify-Access-Token': TOKEN,
              'Content-Type': 'application/json',
            }
          }
        );
        console.log(`🚫 Cancelled Order: ${order.name}`);
      } catch (cancelErr) {
        console.error(`❌ Failed to cancel order ${order.name}:`, cancelErr.response?.data || cancelErr.message);
      }
    }
  } catch (err) {
    console.error('❌ Failed to fetch orders:', err.response?.data || err.message);
  }
})();
