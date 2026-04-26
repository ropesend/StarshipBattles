Add-Type -AssemblyName System.Drawing

$themeRoot = Split-Path -Parent $PSScriptRoot
$skinsDir = Join-Path $themeRoot 'Skins'
$portraitsDir = Join-Path $themeRoot 'Portraits'

$classes = @(
    @{Key='Escort'; Skin='escort.png'; Portrait='Escort_Portrait.jpg'; Scale=.50; Kind='dart'},
    @{Key='Frigate'; Skin='frigate.png'; Portrait='Frigate_Portrait.jpg'; Scale=.60; Kind='spine'},
    @{Key='Destroyer'; Skin='destroyer.png'; Portrait='Destroyer_Portrait.jpg'; Scale=.68; Kind='prongs'},
    @{Key='Light Cruiser'; Skin='light_cruiser.png'; Portrait='LightCruiser_Portrait.jpg'; Scale=.74; Kind='knife'},
    @{Key='Cruiser'; Skin='cruiser.png'; Portrait='Cruiser_Portrait.jpg'; Scale=.80; Kind='swept'},
    @{Key='Heavy Cruiser'; Skin='heavy_cruiser.png'; Portrait='HeavyCruiser_Portrait.jpg'; Scale=.88; Kind='blocks'},
    @{Key='Battle Cruiser'; Skin='battlecruiser.png'; Portrait='BattleCruiser_Portrait.jpg'; Scale=.94; Kind='blade'},
    @{Key='Battleship'; Skin='battleship.png'; Portrait='Battleship_Portrait.jpg'; Scale=1.02; Kind='hammer'},
    @{Key='Dreadnought'; Skin='dreadnought.png'; Portrait='Dreadnought_Portrait.jpg'; Scale=1.10; Kind='fortress'},
    @{Key='Superdreadnought'; Skin='superdreadnought.png'; Portrait='SuperDreadnought_Portrait.jpg'; Scale=1.20; Kind='cathedral'},
    @{Key='Monitor'; Skin='monitor.png'; Portrait='Monitor_Portrait.jpg'; Scale=1.05; Kind='monitor'},
    @{Key='Fighter (Small)'; Skin='small_fighter.png'; Portrait='SmallFighter_Portrait.jpg'; Scale=.34; Kind='fighter_small'},
    @{Key='Fighter (Medium)'; Skin='medium_fighter.png'; Portrait='MediumFighter_Portrait.jpg'; Scale=.43; Kind='fighter_medium'},
    @{Key='Fighter (Large)'; Skin='large_fighter.png'; Portrait='LargeFighter_Portrait.jpg'; Scale=.52; Kind='fighter_large'},
    @{Key='Fighter (Heavy)'; Skin='heavy_fighter.png'; Portrait='HeavyFighter_Portrait.jpg'; Scale=.62; Kind='fighter_heavy'},
    @{Key='Satellite (Small)'; Skin='small_satellite.png'; Portrait='SmallSatellite_Portrait.jpg'; Scale=.38; Kind='satellite_small'},
    @{Key='Satellite (Medium)'; Skin='medium_satellite.png'; Portrait='MediumSatellite_Portrait.jpg'; Scale=.50; Kind='satellite_medium'},
    @{Key='Satellite (Large)'; Skin='large_satellite.png'; Portrait='LargeSatellite_Portrait.jpg'; Scale=.62; Kind='satellite_large'},
    @{Key='Satellite (Heavy)'; Skin='heavy_satellite.png'; Portrait='HeavySatellite_Portrait.jpg'; Scale=.76; Kind='satellite_heavy'}
)

function Brush($a, $r, $g, $b) {
    New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb($a, $r, $g, $b))
}

function Pen($a, $r, $g, $b, $w) {
    New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb($a, $r, $g, $b)), $w
}

function Pt($x, $y) {
    New-Object System.Drawing.PointF ([float]$x), ([float]$y)
}

function FillPoly($g, $brush, $pen, $points) {
    $g.FillPolygon($brush, $points)
    $g.DrawPolygon($pen, $points)
}

function Draw-Core($g, $cx, $cy, $s, $radius) {
    $violet = Brush 235 155 72 255
    $hot = Brush 200 226 210 255
    $g.FillEllipse($violet, $cx - $radius, $cy - $radius, $radius * 2, $radius * 2)
    $g.FillEllipse($hot, $cx - $radius * .34, $cy - $radius * .34, $radius * .68, $radius * .68)
    $g.DrawEllipse((Pen 180 120 92 255 (3 * $s)), $cx - $radius * 1.5, $cy - $radius * 1.5, $radius * 3, $radius * 3)
}

function Draw-Engine($g, $x, $y, $s, $size) {
    $cyan = Brush 190 84 226 255
    $white = Brush 170 230 250 255
    $g.FillEllipse($cyan, $x - $size * .45, $y - $size * .2, $size * .9, $size * 1.25)
    $g.FillEllipse($white, $x - $size * .16, $y + $size * .08, $size * .32, $size * .55)
}

function Draw-Satellite($g, $cx, $cy, $s, $spec) {
    $scale = [float]$spec.Scale
    $r = 260 * $s * $scale
    $hull = Brush 245 20 24 32
    $panel = Brush 235 48 55 68
    $edge = Pen 195 119 234 255 (5 * $s)
    $armPen = Pen 160 70 92 120 (10 * $s)
    $arms = switch ($spec.Kind) {
        'satellite_small' { 3 }
        'satellite_medium' { 4 }
        'satellite_large' { 6 }
        default { 8 }
    }
    for ($i = 0; $i -lt $arms; $i++) {
        $ang = (($i * 360 / $arms) + 15) * [Math]::PI / 180
        $x2 = $cx + [Math]::Cos($ang) * $r * 1.42
        $y2 = $cy + [Math]::Sin($ang) * $r * 1.42
        $g.DrawLine($armPen, $cx, $cy, $x2, $y2)
        $g.DrawLine($edge, $cx, $cy, $x2, $y2)
        $g.FillEllipse($panel, $x2 - $r * .16, $y2 - $r * .16, $r * .32, $r * .32)
    }
    $g.FillEllipse($hull, $cx - $r * .52, $cy - $r * .52, $r * 1.04, $r * 1.04)
    $g.DrawEllipse($edge, $cx - $r * .52, $cy - $r * .52, $r * 1.04, $r * 1.04)
    Draw-Core $g $cx $cy $s ($r * .18)
}

function Draw-Ship($g, $cx, $cy, $s, $spec) {
    if ($spec.Kind.StartsWith('satellite')) {
        Draw-Satellite $g $cx $cy $s $spec
        return
    }

    $scale = [float]$spec.Scale
    $h = 880 * $s * $scale
    $w = 360 * $s * $scale
    $hull = Brush 245 19 23 31
    $panel = Brush 235 48 55 66
    $dark = Brush 220 9 12 18
    $edge = Pen 190 119 234 255 (5 * $s)
    $faint = Pen 120 92 125 150 (3 * $s)

    if ($spec.Kind.StartsWith('fighter')) {
        $h *= .62
        $w *= switch ($spec.Kind) {
            'fighter_small' { .95 }
            'fighter_medium' { 1.25 }
            'fighter_large' { 1.55 }
            default { 1.80 }
        }
        $body = @(
            (Pt $cx ($cy - $h * .50)),
            (Pt ($cx + $w * .20) ($cy - $h * .05)),
            (Pt ($cx + $w * .76) ($cy + $h * .24)),
            (Pt ($cx + $w * .12) ($cy + $h * .34)),
            (Pt $cx ($cy + $h * .50)),
            (Pt ($cx - $w * .18) ($cy + $h * .28)),
            (Pt ($cx - $w * .64) ($cy + $h * .18)),
            (Pt ($cx - $w * .18) ($cy - $h * .07))
        )
        FillPoly $g $hull $edge $body
        Draw-Core $g $cx ($cy + $h * .08) $s (36 * $s * $scale)
        Draw-Engine $g ($cx - $w * .12) ($cy + $h * .42) $s (34 * $s * $scale)
        Draw-Engine $g ($cx + $w * .16) ($cy + $h * .40) $s (34 * $s * $scale)
        return
    }

    $body = switch ($spec.Kind) {
        'dart' {
            @((Pt $cx ($cy-$h*.54)),(Pt ($cx+$w*.22) ($cy-$h*.10)),(Pt ($cx+$w*.16) ($cy+$h*.46)),(Pt $cx ($cy+$h*.56)),(Pt ($cx-$w*.24) ($cy+$h*.24)),(Pt ($cx-$w*.18) ($cy-$h*.16)))
        }
        'spine' {
            @((Pt $cx ($cy-$h*.58)),(Pt ($cx+$w*.18) ($cy-$h*.22)),(Pt ($cx+$w*.28) ($cy+$h*.28)),(Pt ($cx+$w*.06) ($cy+$h*.56)),(Pt ($cx-$w*.12) ($cy+$h*.48)),(Pt ($cx-$w*.22) ($cy-$h*.28)))
        }
        'prongs' {
            @((Pt ($cx-$w*.12) ($cy-$h*.52)),(Pt $cx ($cy-$h*.28)),(Pt ($cx+$w*.14) ($cy-$h*.52)),(Pt ($cx+$w*.34) ($cy+$h*.12)),(Pt ($cx+$w*.10) ($cy+$h*.54)),(Pt ($cx-$w*.24) ($cy+$h*.38)),(Pt ($cx-$w*.38) ($cy+$h*.08)))
        }
        'knife' {
            @((Pt ($cx+$w*.05) ($cy-$h*.60)),(Pt ($cx+$w*.24) ($cy-$h*.18)),(Pt ($cx+$w*.16) ($cy+$h*.56)),(Pt ($cx-$w*.14) ($cy+$h*.44)),(Pt ($cx-$w*.32) ($cy-$h*.12)))
        }
        'swept' {
            @((Pt $cx ($cy-$h*.55)),(Pt ($cx+$w*.30) ($cy-$h*.14)),(Pt ($cx+$w*.82) ($cy+$h*.22)),(Pt ($cx+$w*.20) ($cy+$h*.34)),(Pt ($cx+$w*.06) ($cy+$h*.56)),(Pt ($cx-$w*.28) ($cy+$h*.30)),(Pt ($cx-$w*.70) ($cy+$h*.10)),(Pt ($cx-$w*.22) ($cy-$h*.18)))
        }
        'blocks' {
            @((Pt $cx ($cy-$h*.52)),(Pt ($cx+$w*.34) ($cy-$h*.24)),(Pt ($cx+$w*.42) ($cy+$h*.36)),(Pt ($cx+$w*.12) ($cy+$h*.58)),(Pt ($cx-$w*.36) ($cy+$h*.36)),(Pt ($cx-$w*.32) ($cy-$h*.22)))
        }
        'blade' {
            @((Pt ($cx+$w*.16) ($cy-$h*.62)),(Pt ($cx+$w*.36) ($cy-$h*.16)),(Pt ($cx+$w*.92) ($cy+$h*.06)),(Pt ($cx+$w*.18) ($cy+$h*.28)),(Pt ($cx+$w*.02) ($cy+$h*.58)),(Pt ($cx-$w*.34) ($cy+$h*.18)),(Pt ($cx-$w*.62) ($cy-$h*.04)),(Pt ($cx-$w*.18) ($cy-$h*.24)))
        }
        'hammer' {
            @((Pt $cx ($cy-$h*.50)),(Pt ($cx+$w*.52) ($cy-$h*.24)),(Pt ($cx+$w*.48) ($cy+$h*.40)),(Pt ($cx+$w*.12) ($cy+$h*.58)),(Pt ($cx-$w*.48) ($cy+$h*.34)),(Pt ($cx-$w*.52) ($cy-$h*.20)))
        }
        'fortress' {
            @((Pt $cx ($cy-$h*.54)),(Pt ($cx+$w*.38) ($cy-$h*.32)),(Pt ($cx+$w*.54) ($cy+$h*.42)),(Pt ($cx+$w*.18) ($cy+$h*.62)),(Pt ($cx-$w*.44) ($cy+$h*.44)),(Pt ($cx-$w*.48) ($cy-$h*.28)))
        }
        'cathedral' {
            @((Pt $cx ($cy-$h*.62)),(Pt ($cx+$w*.46) ($cy-$h*.34)),(Pt ($cx+$w*.68) ($cy+$h*.44)),(Pt ($cx+$w*.18) ($cy+$h*.66)),(Pt ($cx-$w*.56) ($cy+$h*.48)),(Pt ($cx-$w*.50) ($cy-$h*.36)))
        }
        'monitor' {
            @((Pt $cx ($cy-$h*.34)),(Pt ($cx+$w*.86) ($cy-$h*.06)),(Pt ($cx+$w*1.10) ($cy+$h*.34)),(Pt ($cx+$w*.18) ($cy+$h*.56)),(Pt ($cx-$w*1.06) ($cy+$h*.30)),(Pt ($cx-$w*.72) ($cy-$h*.10)))
        }
    }

    FillPoly $g $hull $edge $body

    $spine = @(
        (Pt ($cx - $w * .08) ($cy - $h * .38)),
        (Pt ($cx + $w * .13) ($cy - $h * .23)),
        (Pt ($cx + $w * .14) ($cy + $h * .34)),
        (Pt ($cx - $w * .04) ($cy + $h * .47)),
        (Pt ($cx - $w * .20) ($cy + $h * .18)),
        (Pt ($cx - $w * .16) ($cy - $h * .24))
    )
    FillPoly $g $panel $faint $spine

    if ($spec.Kind -in @('blocks','hammer','fortress','cathedral','monitor')) {
        $podW = $w * .26
        $podH = $h * .32
        $g.FillRectangle($dark, $cx - $w * .56, $cy - $h * .02, $podW, $podH)
        $g.DrawRectangle($edge, $cx - $w * .56, $cy - $h * .02, $podW, $podH)
        $g.FillRectangle($dark, $cx + $w * .30, $cy + $h * .02, $podW, $podH)
        $g.DrawRectangle($edge, $cx + $w * .30, $cy + $h * .02, $podW, $podH)
    }

    Draw-Core $g $cx ($cy + $h * .08) $s (42 * $s * $scale)
    Draw-Engine $g ($cx - $w * .15) ($cy + $h * .46) $s (34 * $s * $scale)
    Draw-Engine $g ($cx + $w * .18) ($cy + $h * .45) $s (34 * $s * $scale)

    for ($j = 0; $j -lt 5; $j++) {
        $yy = $cy - $h * .24 + $j * $h * .14
        $g.DrawLine((Pen 120 108 92 148 (2.5 * $s)), $cx - $w * .10, $yy, $cx + $w * .13, $yy + $h * .03)
    }
}

foreach ($spec in $classes) {
    $bmp = New-Object System.Drawing.Bitmap 2048, 2048, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::Transparent)
    Draw-Ship $g 1024 1024 1.0 $spec
    $bmp.Save((Join-Path $skinsDir $spec.Skin), [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()

    $pbmp = New-Object System.Drawing.Bitmap 1024, 1024
    $pg = [System.Drawing.Graphics]::FromImage($pbmp)
    $pg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $pg.Clear([System.Drawing.Color]::FromArgb(8, 8, 14))
    $ringPen = Pen 45 108 92 148 2
    for ($r = 180; $r -le 700; $r += 120) {
        $pg.DrawEllipse($ringPen, 512 - $r / 2, 512 - $r / 2, $r, $r)
    }
    Draw-Ship $pg 512 535 .58 $spec
    $pbmp.Save((Join-Path $portraitsDir $spec.Portrait), [System.Drawing.Imaging.ImageFormat]::Jpeg)
    $pg.Dispose()
    $pbmp.Dispose()
}

$files = Get-ChildItem $skinsDir -Filter *.png | Sort-Object Name
$thumb = 180
$label = 28
$cols = 5
$rows = [Math]::Ceiling($files.Count / $cols)
$sheet = New-Object System.Drawing.Bitmap ([int]($cols * $thumb)), ([int]($rows * ($thumb + $label)))
$sg = [System.Drawing.Graphics]::FromImage($sheet)
$sg.Clear([System.Drawing.Color]::FromArgb(24, 24, 28))
$font = New-Object System.Drawing.Font 'Arial', 8
$brush = [System.Drawing.Brushes]::White
for ($i = 0; $i -lt $files.Count; $i++) {
    $img = [System.Drawing.Image]::FromFile($files[$i].FullName)
    $x = ($i % $cols) * $thumb
    $y = [Math]::Floor($i / $cols) * ($thumb + $label)
    $sg.DrawImage($img, $x, $y, $thumb, $thumb)
    $sg.DrawString($files[$i].Name, $font, $brush, $x + 4, $y + $thumb + 4)
    $img.Dispose()
}
$sheet.Save((Join-Path $PSScriptRoot 'contact_sheet.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$sg.Dispose()
$sheet.Dispose()

Write-Output "Generated $($classes.Count) Voidforged skins, portraits, and contact sheet."
