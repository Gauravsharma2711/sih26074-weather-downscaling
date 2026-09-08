/// Data model for Panchayat Metadata
class PanchayatItem {
  final int panchayatId;
  final int lgdCode;
  final String panchayatName;
  final String blockName;
  final String districtName;
  final double latitude;
  final double longitude;
  final double elevationM;

  PanchayatItem({
    required this.panchayatId,
    required this.lgdCode,
    required this.panchayatName,
    required this.blockName,
    required this.districtName,
    required this.latitude,
    required this.longitude,
    required this.elevationM,
  });

  factory PanchayatItem.fromJson(Map<String, dynamic> json) {
    return PanchayatItem(
      panchayatId: json['panchayat_id'] as int? ?? 1001,
      lgdCode: json['lgd_code'] as int? ?? 0,
      panchayatName: json['panchayat_name'] as String? ?? 'Unknown',
      blockName: json['block_name'] as String? ?? 'Baglan',
      districtName: json['district_name'] as String? ?? 'Nashik',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 20.6,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 74.1,
      elevationM: (json['elevation_m'] as num?)?.toDouble() ?? 550.0,
    );
  }
}
