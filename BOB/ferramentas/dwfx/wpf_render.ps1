param(
    [Parameter(Mandatory)] [string]$Xaml,
    [Parameter(Mandatory)] [string]$Out,
    # full sheet mode
    [double]$Dpi = 55,
    # region mode (sheet millimetres, origin top-left); used when W > 0
    [double]$X = 0, [double]$Y = 0, [double]$W = 0, [double]$H = 0,
    [int]$PixelWidth = 1600
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationCore, PresentationFramework, WindowsBase

$fs = [System.IO.File]::OpenRead($Xaml)
try { $fp = [System.Windows.Markup.XamlReader]::Load($fs) } finally { $fs.Close() }
$pw = $fp.Width; $ph = $fp.Height
$fp.Measure((New-Object System.Windows.Size($pw, $ph)))
$fp.Arrange((New-Object System.Windows.Rect(0, 0, $pw, $ph)))
$fp.UpdateLayout()

if ($W -gt 0) {
    $k = 96 / 25.4
    $rx = $X * $k; $ry = $Y * $k; $rw = $W * $k; $rh = $H * $k
    $outW = $PixelWidth; $outH = [int][math]::Round($rh * $PixelWidth / $rw)
    $vb = New-Object System.Windows.Media.VisualBrush($fp)
    $vb.ViewboxUnits = [System.Windows.Media.BrushMappingMode]::Absolute
    $vb.Viewbox = New-Object System.Windows.Rect($rx, $ry, $rw, $rh)
    $vb.ViewportUnits = [System.Windows.Media.BrushMappingMode]::Absolute
    $vb.Viewport = New-Object System.Windows.Rect(0, 0, $outW, $outH)
    $vb.Stretch = [System.Windows.Media.Stretch]::Fill
    $dv = New-Object System.Windows.Media.DrawingVisual
    $dc = $dv.RenderOpen()
    $r = New-Object System.Windows.Rect(0, 0, $outW, $outH)
    $dc.DrawRectangle([System.Windows.Media.Brushes]::White, $null, $r)
    $dc.DrawRectangle($vb, $null, $r)
    $dc.Close()
    $bmp = New-Object System.Windows.Media.Imaging.RenderTargetBitmap($outW, $outH, 96, 96, [System.Windows.Media.PixelFormats]::Pbgra32)
    $bmp.Render($dv)
} else {
    $outW = [int][math]::Ceiling($pw * $Dpi / 96); $outH = [int][math]::Ceiling($ph * $Dpi / 96)
    $bmp = New-Object System.Windows.Media.Imaging.RenderTargetBitmap($outW, $outH, $Dpi, $Dpi, [System.Windows.Media.PixelFormats]::Pbgra32)
    $bg = New-Object System.Windows.Media.DrawingVisual
    $dc = $bg.RenderOpen()
    $dc.DrawRectangle([System.Windows.Media.Brushes]::White, $null, (New-Object System.Windows.Rect(0, 0, $pw, $ph)))
    $dc.Close()
    $bmp.Render($bg)
    $bmp.Render($fp)
}
$enc = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
$enc.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($bmp))
$ofs = [System.IO.File]::Open($Out, [System.IO.FileMode]::Create)
try { $enc.Save($ofs) } finally { $ofs.Close() }
"OK {0} ({1}x{2} px)" -f $Out, $outW, $outH
