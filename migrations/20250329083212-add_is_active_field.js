module.exports = {
  async up(db, client) {
    await db.collection('songs').updateMany(
      { is_active: { $exists: false } },  // Only update if `is_active` is missing
      { $set: { is_active: true } }       // Default value
    );
  },

  async down(db, client) {
    await db.collection('songs').updateMany(
      {},
      { $unset: { is_active: "" } }
    );
  }
};
