import '../controller/phone_verification_controller.dart';
import 'package:get/get.dart';

class PhoneVerificationBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => PhoneVerificationController());
  }
}
