import '../models/farmer_forecast.dart';
import '../models/panchayat_item.dart';
import '../repositories/farmer_repository.dart';

/// Legacy Service adapter forwarding to the new structured `FarmerRepository`.
class FarmerApiService {
  static final FarmerRepository _repo = FarmerRepository();

  static List<PanchayatItem> get fallbackPanchayats => FarmerRepository.fallbackPanchayats;

  /// Fetch Panchayats List
  static Future<List<PanchayatItem>> getPanchayats() => _repo.getPanchayats();

  /// Fetch hyper-local forecast and verified advisory for farmer
  static Future<FarmerForecast> getForecast(int panchayatId, {String lang = 'en'}) =>
      _repo.getFarmerForecast(panchayatId: panchayatId, lang: lang);
}
