package kr.sqld.study

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.LineBreak
import androidx.compose.ui.text.style.Hyphens
import androidx.compose.ui.text.intl.LocaleList
import androidx.compose.ui.unit.sp
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.shape.RoundedCornerShape

private val Light=lightColorScheme(
    primary=Color(0xFF077580),onPrimary=Color.White,
    primaryContainer=Color(0xFFE5F4F3),onPrimaryContainer=Color(0xFF14535A),
    secondary=Color(0xFF805B16),onSecondary=Color.White,
    secondaryContainer=Color(0xFFFFEBC0),onSecondaryContainer=Color(0xFF624408),
    tertiary=Color(0xFF294E70),onTertiary=Color.White,
    tertiaryContainer=Color(0xFF172D45),onTertiaryContainer=Color(0xFFF5FAFF),
    background=Color(0xFFF5F7FA),onBackground=Color(0xFF172D45),
    surface=Color.White,onSurface=Color(0xFF172D45),
    surfaceVariant=Color(0xFFEAF0F5),onSurfaceVariant=Color(0xFF526477),
    outline=Color(0xFF74869A),outlineVariant=Color(0xFFDCE4EC),
    error=Color(0xFFAC302D),errorContainer=Color(0xFFFFE1DC),onErrorContainer=Color(0xFF601614))
private val Dark=darkColorScheme(
    primary=Color(0xFF86D9DC),onPrimary=Color(0xFF00383F),
    primaryContainer=Color(0xFF123F49),onPrimaryContainer=Color(0xFFC8F1F0),
    secondary=Color(0xFFF2CF83),onSecondary=Color(0xFF3D2C07),
    secondaryContainer=Color(0xFF4E4026),onSecondaryContainer=Color(0xFFFFE5B1),
    tertiary=Color(0xFFADCCE8),onTertiary=Color(0xFF19334C),
    tertiaryContainer=Color(0xFF203B55),onTertiaryContainer=Color(0xFFF0F7FF),
    background=Color(0xFF101A26),onBackground=Color(0xFFE8EFF7),
    surface=Color(0xFF182635),onSurface=Color(0xFFE8EFF7),
    surfaceVariant=Color(0xFF26384A),onSurfaceVariant=Color(0xFFB8C7D7),
    outline=Color(0xFF8296AD),outlineVariant=Color(0xFF34495E),
    error=Color(0xFFFFB4AB),errorContainer=Color(0xFF642A28),onErrorContainer=Color(0xFFFFDAD5))
@Composable fun SqlNoteTheme(dark:Boolean,scale:Float,content:@Composable ()->Unit){
    fun style(size:Int,weight:FontWeight=FontWeight.Normal)=TextStyle(fontFamily=FontFamily.SansSerif,fontSize=(size*scale).sp,lineHeight=(size*(if(weight==FontWeight.Normal)1.55 else 1.35)*scale).sp,fontWeight=weight,localeList=LocaleList("ko-KR"),hyphens=Hyphens.None,lineBreak=if(weight==FontWeight.Normal)LineBreak.Paragraph.copy(strategy=LineBreak.Strategy.Balanced,wordBreak=LineBreak.WordBreak.Phrase) else LineBreak.Heading)
    MaterialTheme(colorScheme=if(dark)Dark else Light,
        shapes=Shapes(extraSmall=RoundedCornerShape(6.dp),small=RoundedCornerShape(10.dp),medium=RoundedCornerShape(14.dp),large=RoundedCornerShape(20.dp),extraLarge=RoundedCornerShape(24.dp)),
        typography=Typography(displaySmall=style(32,FontWeight.Bold),headlineLarge=style(28,FontWeight.Bold),headlineMedium=style(25,FontWeight.Bold),headlineSmall=style(22,FontWeight.SemiBold),titleLarge=style(20,FontWeight.SemiBold),titleMedium=style(18,FontWeight.SemiBold),titleSmall=style(16,FontWeight.SemiBold),bodyLarge=style(17),bodyMedium=style(16),bodySmall=style(13),labelLarge=style(14,FontWeight.SemiBold),labelMedium=style(12,FontWeight.Medium)),content=content)
}
