import 'package:flutter_test/flutter_test.dart';
import 'package:farmer_app/main.dart';

void main() {
  testWidgets('GramSevak Farmer App renders correctly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const GramSevakFarmerApp());
    await tester.pumpAndSettle();

    // Verify that the title and key branding elements appear.
    expect(find.text('GramSevak'), findsWidgets);
    expect(find.text('Forecast'), findsWidgets);
    expect(find.text('Advisory'), findsWidgets);
    expect(find.text('Profile'), findsOneWidget);
  });
}
